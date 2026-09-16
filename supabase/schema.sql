create table public.hcl_receipts (
  run_id uuid primary key,
  bundle jsonb not null check (jsonb_typeof(bundle) = 'object'),
  sha256 text not null check (sha256 ~ '^[0-9a-f]{64}$'),
  stored_at timestamptz not null default now(),
  constraint receipt_run_match check ((bundle->>'run_id') is not null and bundle->>'run_id' = run_id::text)
);
alter table public.hcl_receipts enable row level security;
revoke all on public.hcl_receipts from public, anon, authenticated, service_role;
grant select, insert on public.hcl_receipts to service_role;
comment on table public.hcl_receipts is 'i Ecosystem research receipts. Backend append-only privileges; not a trusted timestamp or legal clearance. Administrators retain control.';
