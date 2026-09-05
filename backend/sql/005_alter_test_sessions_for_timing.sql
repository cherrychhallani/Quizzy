alter table test_sessions
  add column if not exists started_at timestamptz,
  add column if not exists completed_at timestamptz;

alter table test_sessions
  drop constraint if exists test_sessions_status_check;

alter table test_sessions
  add constraint test_sessions_status_check
  check (status in ('not_started', 'in_progress', 'completed', 'expired'));