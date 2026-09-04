-- Run this in the Supabase SQL editor (Project -> SQL Editor -> New query)
-- Creates the "documents" table used by Step 1: Exam/Class Selection & Upload

create table if not exists documents (
    document_id uuid primary key default gen_random_uuid(),
    user_id uuid not null,                -- will match Supabase Auth user id later
    exam text not null check (exam in ('JEE', 'NEET', 'OTHER')),
    class text not null check (class in ('11', '12')),
    subject text,                         -- optional, per the "Subject Selection" decision (nullable for now)
    file_url text not null,
    file_type text not null check (file_type in ('pdf', 'jpg', 'jpeg', 'png')),
    status text not null default 'uploaded',
    created_at timestamptz not null default now()
);

-- Helpful index for listing a user's documents later
create index if not exists idx_documents_user_id on documents (user_id);
