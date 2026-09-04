# AI-Powered Practice Test Generator

Converts an uploaded question paper (PDF or photo) into structured,
topic-tagged questions using OCR + an LLM. Built around NEET/JEE, Class 11/12,
NCERT-based topics.

**Current status: Steps 1–3 of the roadmap are complete.** Step 4 (test
configuration & assembly) is next.

---

## Architecture

- **Frontend:** Next.js + Tailwind CSS (`practice-test-frontend/`)
- **Backend:** FastAPI (`backend/`)
- **Database + Storage + Auth (future):** Supabase (Postgres + Storage)
- **OCR:** PyMuPDF (text-based PDFs), Tesseract + OpenCV preprocessing (images)
- **LLM structuring:** Gemini API, schema-constrained JSON output

```
.
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI app, router registration
│   │   ├── config.py          # env-based settings
│   │   ├── database.py        # Supabase client
│   │   ├── models.py          # Pydantic schemas
│   │   ├── topics.py          # predefined NCERT topic lists
│   │   ├── routes/
│   │   │   ├── upload.py      # Step 1
│   │   │   ├── extract.py     # Step 2
│   │   │   └── structure.py   # Step 3
│   │   └── services/
│   │       ├── extraction.py       # PyMuPDF / OCR logic
│   │       └── llm_structuring.py  # Gemini prompt + validation
│   ├── sql/
│   │   ├── 001_create_documents_table.sql
│   │   ├── 002_add_extracted_text_column.sql
│   │   └── 003_create_questions_table.sql
│   ├── requirements.txt
│   └── .env.example
└── practice-test-frontend/
    ├── app/upload/page.tsx
    ├── components/UploadForm.tsx
    └── lib/api.ts
```

---

## Setup

### 1. Supabase

1. Create a project at https://supabase.com.
2. **Settings → API**: copy `Project URL` and the `service_role` key.
3. **Storage**: create a public bucket named `question-papers`.
4. **SQL Editor**: run the three files in `backend/sql/` **in order**
   (001, then 002, then 003).

### 2. Gemini

Get a free API key at https://aistudio.google.com/app/apikey.

### 3. Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# fill in SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, GEMINI_API_KEY
```

Run:
```bash
uvicorn app.main:app --reload --port 8000
```

### 4. Frontend

```bash
cd practice-test-frontend
npm install
echo "NEXT_PUBLIC_API_BASE_URL=http://localhost:8000" > .env.local
npm run dev
```

Open http://localhost:3000/upload.

---

## API Endpoints (current)

| Method | Path | Step | Purpose |
|---|---|---|---|
| POST | `/api/upload` | 1 | Upload a file, validate it, create a `documents` row |
| POST | `/api/documents/{document_id}/extract-text` | 2 | Extract raw text (PyMuPDF or OCR), update status |
| POST | `/api/documents/{document_id}/structure` | 3 | LLM-structure the text into `questions` rows |
| GET | `/health` | — | Health check |

Interactive docs (and the fastest way to test file uploads without fighting
curl/PowerShell): http://localhost:8000/docs

---

## Known limitations (intentional, documented in the project doc)

- **Scanned photo saved as `.pdf`:** the extension check will treat it as a
  text PDF and PyMuPDF will return little/no text. No OCR fallback yet —
  accepted v1 gap.
- **Topic tagging** is currently wired for **NEET, Class 11, Biology only**.
  Other exam/class/subject combinations will 400 at the `/structure`
  endpoint until their topic lists are added to `app/topics.py`.
- **No manual review step** before testing — by design. A lightweight
  automated validation pass drops malformed questions instead (see
  `filter_malformed` in `llm_structuring.py`).
- **`user_id`** is a hardcoded placeholder UUID everywhere until Supabase
  Auth (phone/OTP) is implemented in a later step.

---

## Roadmap

- [x] Step 1 — Exam/Class Selection & Upload
- [x] Step 2 — Extract Text
- [x] Step 3 — LLM-Based Question Structuring
- [ ] Step 4 — Test Configuration & Assembly
- [ ] Step 5 — Timed Test-Taking
- [ ] Step 6 — Auto-Grading
- [ ] Step 7 — Results & Analytics
- [ ] Step 8 — History Dashboard
- [ ] Step 9 — AI Chat Tutor
