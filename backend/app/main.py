from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import upload, extract, structure, tests

app = FastAPI(title="Practice Test Generator API")

# Allow the Next.js dev server to call this API during local development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(extract.router, prefix="/api", tags=["extract"])
app.include_router(structure.router, prefix="/api", tags=["structure"])
app.include_router(tests.router, prefix="/api", tags=["tests"])

@app.get("/health")
def health():
    return {"status": "ok"}
