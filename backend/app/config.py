from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    supabase_url: str
    supabase_service_role_key: str
    supabase_storage_bucket: str = "question-papers"

    max_file_size_mb: int = 15
    max_pdf_pages: int = 20

    gemini_api_key: str
    gemini_model: str = "gemini-3.6-flash"

    class Config:
        env_file = ".env"


settings = Settings()
