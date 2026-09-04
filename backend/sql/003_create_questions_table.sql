create table if not exists questions (
    question_id uuid primary key default gen_random_uuid(),
    document_id uuid not null references documents(document_id),
    question_text text not null,
    type text not null check (type in ('mcq', 'numerical')),
    options jsonb,
    answer text,
    topic text not null,
    difficulty text not null check (difficulty in ('easy', 'medium', 'hard')),
    created_at timestamptz not null default now()
);

create index if not exists idx_questions_document_id on questions (document_id);