create table if not exists test_sessions (
    session_id uuid primary key default gen_random_uuid(),
    user_id uuid not null,
    question_ids jsonb not null,
    time_limit_seconds integer not null,
    status text not null default 'not_started' check (status in ('not_started', 'in_progress', 'completed')),
    created_at timestamptz not null default now()
);

create index if not exists idx_test_sessions_user_id on test_sessions (user_id);