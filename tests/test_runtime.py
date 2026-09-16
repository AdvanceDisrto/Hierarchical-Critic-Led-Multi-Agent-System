import asyncio
import hashlib
from uuid import uuid4
import pytest
from pydantic import ValidationError
from hcl.models import Plan, Artifact, Review, Evidence, Chirp
from hcl.bus import ThoughtBus
from hcl.engine import Director, digest
from hcl.cli import export

SUBS = ['thermofluids','microgrid','orchestration_software']
class FakeAgent:
    def __init__(self, fail=False):
        self.active=0
        self.peak=0
        self.fail=fail
    async def execute(self,role,payload,schema):
        self.active+=1
        self.peak=max(self.peak,self.active)
        try:
            await asyncio.sleep(0.005)
            if schema is Plan:
                return Plan(rationale='test',assignments=[{'subsystem':s,'objective':'test','metrics':[]} for s in SUBS])
            if schema is Artifact:
                if self.fail:
                    raise RuntimeError('provider down')
                return Artifact(subsystem=payload['assignment']['subsystem'],title='test',abstract='test',description='test',specifications=[],claims=[],trademarks=[])
            return Review(status='PASSED',reasoning='test only',remedies=[],evidence_ids=['patent','engineering'])
        finally:
            self.active-=1

def evidence():
    return [Evidence(id=k,kind=k,source_url='https://example.com/test',retrieved_at='2026-09-16T00:00:00Z',query='test fixture',excerpt='fixture',content_sha256=hashlib.sha256(b'fixture').hexdigest()) for k in ['patent','engineering']]

def run(tmp_path, sources, fail=False):
    async def execute():
        bus=ThoughtBus(tmp_path/'db',str(uuid4()))
        agent=FakeAgent(fail)
        try:
            bundle=await Director(agent,bus,sources,max_loops=2).run('Telepath waterless cooling')
            return bundle,agent
        finally:
            bus.close()
    return asyncio.run(execute())

def test_missing_evidence_blocks_even_when_models_pass(tmp_path):
    b,a=run(tmp_path,[])
    assert b['payload']['status']=='BLOCKED'
    assert len(b['payload']['history'])==2
    assert a.peak>=3

def test_concurrent_committee_and_export(tmp_path):
    b,a=run(tmp_path,evidence())
    assert b['payload']['status']=='REVIEW_READY'
    assert a.peak==6
    assert b['sha256']==digest(b['payload'])
    folder=export(b,tmp_path/'exports')
    assert (folder/'disclosure.md').exists()
    with pytest.raises(FileExistsError): export(b,tmp_path/'exports')
    b['payload']['status']='tampered'
    with pytest.raises(ValueError): export(b,tmp_path/'bad')

def test_provider_failure_cancels_siblings(tmp_path):
    b,a=run(tmp_path,[],True)
    assert b['payload']['status']=='FAILED'
    assert a.active==0

def test_plan_completeness():
    with pytest.raises(ValidationError): Plan(rationale='empty',assignments=[])
    with pytest.raises(ValidationError): Plan(rationale='duplicates',assignments=[{'subsystem':'microgrid','objective':'x','metrics':[]}]*3)

def test_priority_replay_isolation_and_backpressure(tmp_path):
    async def execute():
        bus=ThoughtBus(tmp_path/'bus','run',capacity=2)
        seen=[]
        async def listen(event): seen.append(event.event)
        bus.register_ear('global_broadcast',listen)
        def chirp(event,run='run'):
            return Chirp(id=str(uuid4()),run_id=run,sender='test',frequency='global_broadcast',event=event,timestamp=1)
        first=chirp('ring')
        assert await bus.broadcast_chirp(first)
        assert not await bus.broadcast_chirp(first)
        await bus.broadcast_chirp(chirp('rejection_alert'))
        assert bus.halted.is_set()
        with pytest.raises(asyncio.QueueFull): await bus.broadcast_chirp(chirp('ring'))
        with pytest.raises(ValueError): await bus.broadcast_chirp(chirp('ring','other'))
        assert await bus.drain()==[]
        assert seen==['rejection_alert','ring']
        bus.close()
        reopened=ThoughtBus(tmp_path/'bus','run')
        assert len(reopened.replay())==2
        assert len(reopened.replay(after=1))==1
        reopened.close()
    asyncio.run(execute())

def test_listener_failure_is_reported_without_losing_other_listener(tmp_path):
    async def execute():
        bus=ThoughtBus(tmp_path/'bus','run')
        seen=[]
        async def broken(e): raise ValueError('bad')
        async def healthy(e): seen.append(e.id)
        bus.register_ear('global_broadcast',broken)
        bus.register_ear('global_broadcast',healthy)
        await bus.broadcast_chirp(Chirp(id='x',run_id='run',sender='test',frequency='global_broadcast',event='ring',timestamp=1))
        assert await bus.drain()==['ValueError']
        assert seen==['x']
        bus.close()
    asyncio.run(execute())

def test_evidence_hash_rejected(tmp_path):
    bus=ThoughtBus(tmp_path/'db','run')
    sources=evidence()
    sources[0].excerpt='modified'
    with pytest.raises(ValueError): Director(FakeAgent(),bus,sources)
    bus.close()

def test_provider_handles_refusal_and_invalid_json():
    import httpx
    from hcl.providers import NativeAgent
    async def execute():
        agent=NativeAgent('https://example.com/v1','test','native-model')
        await agent.client.aclose()
        for message in [{'refusal':'no','content':None},{'content':'not-json'}]:
            agent.client=httpx.AsyncClient(base_url='https://example.com/v1/',transport=httpx.MockTransport(lambda r: httpx.Response(200,json={'choices':[{'finish_reason':'stop','message':message}]})))
            with pytest.raises(ValueError): await agent.execute('critic',{},Review)
            await agent.close()
    asyncio.run(execute())

def test_supabase_conflicting_receipt_is_rejected():
    import httpx
    from hcl.providers import SupabaseStore
    async def execute():
        store=SupabaseStore('https://example.com','sb_secret_test')
        await store.client.aclose()
        def respond(request):
            if request.method=='POST': return httpx.Response(409)
            return httpx.Response(200,json=[{'sha256':'different','bundle':{}}])
        store.client=httpx.AsyncClient(base_url='https://example.com/rest/v1/',transport=httpx.MockTransport(respond))
        with pytest.raises(ValueError): await store.save(str(uuid4()),{},'a'*64)
        await store.close()
    asyncio.run(execute())
