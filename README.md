# Hierarchical-Critic-Led-Multi-Agent-System
A Hierarchical Critic-Led Multi-Agent System uses a master Director AI to orchestrate specialized engineer agents. An adversarial Super-Critic Committee reviews every schematic against global patent/trademark databases using real-time pub/sub telepathic data channels to build the most unique, breakthrough infrastructure ever made

---

## i Ecosystem implementation

The description above captures the original vision. The implementation now provides a tested research runtime; it does not guarantee breakthrough IP or global registry clearance.

| Component | Implemented behavior |
|---|---|
| Director | Exactly three assignments, bounded replanning, full attempt history |
| Workers | Concurrent thermofluids, microgrid, and orchestration software generation |
| Committee | Six concurrent reviews; missing evidence blocks readiness |
| Telepath bus | Local priority dispatch, halt signal, SQLite replay, run isolation |
| Model adapter | Async OpenAI-compatible endpoint; configurable native model |
| Export | JSON + Markdown research disclosure and reproducible SHA-256 |
| Supabase | Backend-only append-only receipt table and REST adapter |

**Telepath waterless cooling remains the cooling constraint.** No live model, patent registry, cooling equipment, power controller, or blockchain is activated by installing this package.

### Windows: one-play verification

From your chosen project parent directory:

```powershell
git clone --branch feat/director-telepath-runtime https://github.com/AdvanceDisrto/Hierarchical-Critic-Led-Multi-Agent-System.git
if ($LASTEXITCODE -ne 0) { throw 'Clone failed; use your existing checkout if present.' }
Set-Location Hierarchical-Critic-Led-Multi-Agent-System
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\Test-OnePlay.ps1
```

Requires Python 3.11+ and Git. The script creates an isolated environment and fails on installation or test errors.

### Live research run

Set `NATIVE_API_BASE` to your native model's OpenAI-compatible `/v1` URL, `NATIVE_API_KEY` to its credential, and `NATIVE_MODEL` to its actual served model identifier. If the base is omitted, the adapter uses the OpenAI API. The endpoint must support strict JSON Schema structured outputs. No model name or credential is guessed.

```powershell
& .\.venv\Scripts\python.exe -m hcl.cli `
  --directive 'Design the i Ecosystem private cloud using Telepath waterless cooling, predictive microgrid routing, and bare-metal orchestration.' `
  --evidence .\evidence.json `
  --max-loops 4
```

The evidence file is a JSON array matching `hcl.models.Evidence`: `id`, `kind` (patent/trademark/engineering), `source_url`, `retrieved_at`, `query`, `excerpt`, and `content_sha256` (SHA-256 of the UTF-8 excerpt). Preserve primary-source provenance. Omitting evidence runs research generation but blocks REVIEW_READY.

For Supabase persistence, set `SUPABASE_URL` and the backend-only `SUPABASE_SECRET_KEY`, then add `--supabase`. The receipt schema is installed in BUDDY; `supabase/schema.sql` records its definition. Do not expose the backend key to a browser. Local exports remain available if a remote write fails.

Exit codes: 0 = REVIEW_READY research draft; 2 = BLOCKED or FAILED run; unhandled configuration/storage errors also exit nonzero. Outputs live under `runs/<run UUID>/`; these and credentials are git-ignored.

### Scope and evidence

- Legal research status is preliminary; no automated patent/trademark clearance or filing occurs.
- Registry acquisition currently uses operator-supplied evidence, not fabricated searches.
- Bus dispatch is local and cooperative, not instantaneous distributed communication.
- Receipt hashing detects modification; it does not establish ownership or trusted creation time.
- CI tests runtime behavior with synthetic fixtures. A live model and hardware validation are separate gates.

Read the [technical whitepaper](docs/WHITEPAPER.md) for architecture, trust boundaries, failure semantics, and remaining deployment work.
