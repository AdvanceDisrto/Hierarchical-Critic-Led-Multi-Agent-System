import asyncio
import hashlib
import json
import time
from uuid import uuid4
from .models import Plan, Artifact, Review, Chirp, SUBSYSTEMS

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode('utf-8')

def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()

class Director:
    def __init__(self, agent, bus, evidence, max_loops=4, stage_timeout=180):
        if not 1 <= max_loops <= 10:
            raise ValueError('max_loops must be 1..10')
        if len({e.id for e in evidence}) != len(evidence):
            raise ValueError('Duplicate evidence IDs')
        for e in evidence:
            if hashlib.sha256(e.excerpt.encode()).hexdigest() != e.content_sha256:
                raise ValueError('Evidence excerpt hash mismatch')
        self.agent, self.bus, self.evidence = agent, bus, evidence
        self.max_loops, self.timeout = max_loops, stage_timeout

    async def call(self, role, payload, schema):
        return await asyncio.wait_for(self.agent.execute(role, payload, schema), self.timeout)

    async def parallel(self, calls):
        async with asyncio.TaskGroup() as group:
            tasks = [group.create_task(c) for c in calls]
        return [t.result() for t in tasks]

    async def run(self, directive):
        if not directive.strip():
            raise ValueError('Empty directive')
        history = []
        evidence = [e.model_dump() for e in self.evidence]
        try:
            for loop in range(1, self.max_loops+1):
                self.bus.halted.clear()  # Only Director starts a new attempt.
                plan = await self.call('Director: produce exactly three cohesive assignments. Address previous review failures.', {'directive':directive,'history':history,'constraint':'Telepath waterless cooling'}, Plan)
                artifacts = await self.parallel([
                    self.call('Invention engineer: '+a.subsystem, {'directive':directive,'plan':plan.model_dump(),'assignment':a.model_dump(),'evidence':evidence,'telemetry':[e.model_dump() for _,e in self.bus.replay()]}, Artifact)
                    for a in plan.assignments])
                if {a.subsystem for a in artifacts} != SUBSYSTEMS or any(a.subsystem != task.subsystem for a,task in zip(artifacts,plan.assignments)):
                    raise ValueError('Worker subsystem mismatch')
                for a in artifacts:
                    await self.bus.broadcast_chirp(Chirp(id=str(uuid4()),run_id=self.bus.run_id,sender=a.subsystem,frequency={'thermofluids':'thermofluid_telemetry','microgrid':'grid_load_signals','orchestration_software':'software_heartbeat'}[a.subsystem],event='data_dump',payload=a.model_dump(),timestamp=time.time()))
                if await self.bus.drain():
                    raise RuntimeError('Telemetry listener failed')
                reviews = await self.parallel([
                    self.call(role+' critic: review the full system, interfaces, and each assigned artifact. PASSED means preliminary review only. Missing sources require NEEDS_EVIDENCE.', {'artifact':a.model_dump(),'system':[v.model_dump() for v in artifacts],'evidence':evidence}, Review)
                    for a in artifacts for role in ('Legal','Engineering')])
                known = {e.id:e for e in self.evidence}
                for index, review in enumerate(reviews):
                    needed = {'patent'} if index % 2 == 0 else {'engineering'}
                    artifact = artifacts[index//2]
                    if index % 2 == 0 and artifact.trademarks:
                        needed.add('trademark')
                    cited = {known[i].kind for i in review.evidence_ids if i in known}
                    spec_refs_valid = all(s.evidence_ids and all(i in known and known[i].kind == 'engineering' for i in s.evidence_ids) for s in artifact.specifications if s.basis != 'target')
                    if not needed <= cited or any(i not in known for i in review.evidence_ids) or not spec_refs_valid:
                        review.status = 'NEEDS_EVIDENCE'
                        review.reasoning = 'Required traceable sources or engineering evidence missing. '+review.reasoning
                cleared = all(r.status == 'PASSED' for r in reviews) and not self.bus.halted.is_set()
                history.append({'loop':loop,'plan':plan.model_dump(),'artifacts':[a.model_dump() for a in artifacts],'reviews':[r.model_dump() for r in reviews]})
                if cleared:
                    return self.bundle(directive, history, 'REVIEW_READY')
                await self.bus.broadcast_chirp(Chirp(id=str(uuid4()),run_id=self.bus.run_id,sender='committee',frequency='global_broadcast',event='rejection_alert',payload={'loop':loop,'reviews':[r.model_dump() for r in reviews]},timestamp=time.time()))
                if await self.bus.drain():
                    raise RuntimeError('Alarm listener failed')
            return self.bundle(directive, history, 'BLOCKED')
        except Exception as exc:
            return self.bundle(directive, history, 'FAILED', type(exc).__name__)

    def bundle(self, directive, history, status, error=None):
        body = {'schema_version':1,'run_id':self.bus.run_id,'directive':directive,'status':status,'error':error,'history':history,'evidence':[e.model_dump() for e in self.evidence],'events':[e.model_dump() for _,e in self.bus.replay()],'created_at':time.time(),'scope':'Research draft; no legal clearance, hardware certification, or trusted timestamp'}
        return {'payload':body,'sha256':digest(body)}
