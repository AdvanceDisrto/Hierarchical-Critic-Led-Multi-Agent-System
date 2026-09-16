"""Bounded local priority dispatch plus SQLite event replay. No zero-latency claim."""
import asyncio
import itertools
import json
import sqlite3
from .models import Chirp

class ThoughtBus:
    def __init__(self, path, run_id, capacity=256, listener_timeout=10):
        self.run_id = run_id
        self.db = sqlite3.connect(path)
        self.db.execute('CREATE TABLE IF NOT EXISTS events (seq INTEGER PRIMARY KEY AUTOINCREMENT, id TEXT UNIQUE NOT NULL, run_id TEXT NOT NULL, body TEXT NOT NULL)')
        self.queue = asyncio.PriorityQueue(maxsize=capacity)
        self.counter = itertools.count()
        self.listeners = {}
        self.timeout = listener_timeout
        self.halted = asyncio.Event()

    def register_ear(self, frequency, callback):
        if frequency not in {'thermofluid_telemetry','grid_load_signals','software_heartbeat','global_broadcast'}:
            raise ValueError('Unknown frequency')
        self.listeners.setdefault(frequency, []).append(callback)

    async def broadcast_chirp(self, chirp):
        if chirp.run_id != self.run_id:
            raise ValueError('Cross-run event rejected')
        body = chirp.model_dump_json()
        row = self.db.execute('SELECT body FROM events WHERE id=?', (chirp.id,)).fetchone()
        if row:
            if row[0] != body:
                raise ValueError('Event ID collision')
            return False
        if self.queue.full():
            raise asyncio.QueueFull('Backpressure: drain and retry')
        with self.db:
            self.db.execute('INSERT INTO events(id,run_id,body) VALUES(?,?,?)', (chirp.id,chirp.run_id,body))
        if chirp.event == 'rejection_alert':
            self.halted.set()
        self.queue.put_nowait((0 if chirp.event == 'rejection_alert' else 1, next(self.counter), chirp))
        return True

    async def drain(self):
        failures = []
        while not self.queue.empty():
            _, _, event = self.queue.get_nowait()
            try:
                callbacks = self.listeners.get(event.frequency, [])
                outcomes = await asyncio.gather(*(asyncio.wait_for(cb(event.model_copy(deep=True)), self.timeout) for cb in callbacks), return_exceptions=True)
                failures.extend(type(e).__name__ for e in outcomes if isinstance(e, BaseException))
            finally:
                self.queue.task_done()
        return failures

    def replay(self, after=0):
        return [(seq, Chirp.model_validate_json(body)) for seq, body in self.db.execute('SELECT seq,body FROM events WHERE run_id=? AND seq>? ORDER BY seq', (self.run_id,after))]

    def close(self):
        self.db.close()
