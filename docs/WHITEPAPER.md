# i Ecosystem — Hierarchical Critic-Led Research Runtime

Version 0.1.0 · September 16, 2026

## Purpose

A human supplies one directive to a Director. The Director creates exactly one assignment each for thermofluids, microgrid, and orchestration software. Workers produce structured research artifacts concurrently. A legal research critic and an engineering critic independently review every artifact with full system context. Rejections return to the Director for bounded replanning.

Telepath waterless cooling is a required project constraint. This repository does not establish its physical mechanism or measured performance. Cooling specifications distinguish targets, calculations, and measurements. No fluid formulation, 800 V hardware actuation, reactor control, or generated source code is executed by this runtime.

## Runtime and state

The native Python implementation uses asyncio TaskGroup and explicit state transitions rather than an additional graph framework. Each worker owns its result; shared dictionaries are assembled only after successful completion. Exceptions cancel sibling tasks. Stage deadlines and a maximum of ten iterations bound resource use. The default is four attempts; HTTP retries are limited to three for designated transient status codes. Connection errors fail the attempt.

Director → concurrent invention → concurrent committee → review-ready, replan, or blocked. Provider and validation errors produce FAILED research receipts. State includes every completed attempt, source record, and recorded event. Intermediate work from a partially failed worker stage is not a completed attempt.

## Telepath event semantics

ThoughtBus provides a bounded in-process priority queue and SQLite event history, with run isolation, unique event IDs, collision detection, listener deadlines, replay cursors, and independent listener failure reporting. Rejection alerts set a cooperative halt signal immediately and precede queued ordinary events. They cannot interrupt synchronous code or retract an already executed action.

Dispatch occurs at explicit drain points. This is not a distributed broker or an always-running cross-host transport. Replay retrieves historical events but does not automatically invoke callbacks; consumers own durable acknowledgement cursors. No exactly-once delivery or zero latency is claimed. Model workers receive event history as untrusted context on subsequent Director attempts. No real hardware telemetry source is connected by default.

## Evidence and critics

Evidence records carry source URLs, retrieval timestamps, search queries, excerpts, and SHA-256 hashes of those excerpts. The runtime verifies excerpt integrity and cited IDs. Patent evidence is required for legal research review; trademark evidence is additionally required for artifacts with proposed names. Engineering evidence is required for engineering review and non-target specification references.

These checks prove traceability within the supplied record set, not authenticity or exhaustive coverage. An operator must source and review evidence. There is no simulated registry in live execution and no invented Google Patents or WIPO API endpoint. Automated patent/trademark retrieval is not yet connected. REVIEW_READY means preliminary research review, never patentability, freedom to operate, trademark availability, or authorization to file. Markdown exports are disclosure drafts for human review, not USPTO filing packages.

## Persistence and trust boundary

Canonical UTF-8 JSON uses sorted keys, compact separators, and rejects nonfinite numbers. The payload digest covers directive, attempts, evidence, event history, status, and a local wall-clock timestamp. A digest detects changes when compared against a trusted copy; it is not a digital signature, proof of ownership, blockchain anchor, or trusted timestamp.

Exports use a UUID folder and refuse to overwrite existing runs. Supabase receipts have RLS enabled, no client grants, and backend SELECT/INSERT privileges only. Backend updates and deletes are denied. Database administrators retain authority; administrative immutability and external timestamp anchoring are future integrations. Credentials are read from environment variables and never written into exports.

## Validation and operational limits

Automated tests use explicitly synthetic agents and evidence to exercise concurrent execution, committee gating, bounded rejection loops, worker failure, input validation, event priority/backpressure, replay, isolation, listener failure, digest tampering, provider refusals, malformed outputs, and conflicting Supabase receipts.

Live native-model inference requires an explicitly selected endpoint, key, and model. Tests do not validate physical designs or production capacity. Multi-host delivery, consumer leases, human approval UI, live registry retrieval, and trusted evidence attestation remain deployment work.

## References

- [Supabase API grants and RLS](https://supabase.com/docs/guides/api/securing-your-api)
- [OpenAI structured outputs and refusal handling](https://developers.openai.com/api/docs/guides/structured-outputs)
- [Python TaskGroup cancellation semantics](https://docs.python.org/3/library/asyncio-task.html#task-groups)
