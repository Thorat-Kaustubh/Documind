import os
from supabase import create_client, Client

class SupabaseService:
    """
    Supabase Service: Handles Auth integration and high-level table operations.
    """
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
        self.client: Client = None
        
        if self.url and self.key and "your_supabase" not in self.url:
            try:
                self.client = create_client(self.url, self.key)
                print("✅ Supabase Client Initialized")
            except Exception as e:
                print(f"❌ Supabase Init Error: {e}")
        else:
            print("⚠️ Supabase credentials missing or invalid in .env")

    def get_user_profile(self, user_id: str):
        if not self.client: return None
        return self.client.table("profiles").select("*").eq("id", user_id).execute()

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    service = SupabaseService()
