# Verification receipt — September 16, 2026

- Local runtime suite: **9 passed**, Python 3.12.
- CLI help and Git whitespace checks: passed.
- Live Supabase project: BUDDY.
- `hcl_receipts` schema applied successfully.
- RLS verified enabled.
- Anonymous and authenticated clients: no SELECT, INSERT, UPDATE, or DELETE grants.
- Service role: SELECT and INSERT only; UPDATE and DELETE denied.
- Transactional service-role insert check completed and rolled back; zero test rows retained.
- Supabase security advisor: informational `rls_enabled_no_policy` for this table is intentional because all client grants are denied and only the trusted backend uses it. [Advisor explanation](https://supabase.com/docs/guides/database/database-linter?lint=0008_rls_enabled_no_policy).

No live native-model call, patent/trademark registry query, external timestamp anchor, or hardware experiment was performed. HTTP adapter tests use mocked transport. Windows verification is included in CI and the supplied PowerShell script; it was not executed on the user's machine.
