from supabase import create_client, Client
from app.config import settings

# Server-side client using the service role key.
# NEVER expose the service role key to the frontend — it bypasses row-level security.
supabase: Client = create_client(
    settings.supabase_url,
    settings.supabase_service_role_key,
)
