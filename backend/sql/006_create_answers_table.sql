create table if not exists answers (
    answer_id uuid primary key default gen_random_uuid(),
    session_id uuid not null references test_sessions(session_id),
    question_id uuid not null references questions(question_id),
    student_answer text,
    time_spent_seconds integer not null default 0,
    is_correct boolean,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    unique (session_id, question_id)
);

create index if not exists idx_answers_session_id on answers (session_id);