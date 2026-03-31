import os
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Initialize Supabase client for backend verification
supabase_url = os.getenv("SUPABASE_URL")
supabase_anon_key = os.getenv("SUPABASE_ANON_KEY")

if not supabase_url or not supabase_anon_key:
    raise RuntimeError("Missing SUPABASE credentials in environment.")

supabase: Client = create_client(supabase_url, supabase_anon_key)

security = HTTPBearer()

async def get_current_user(auth: HTTPAuthorizationCredentials = Depends(security)):
    """
    Verifies the Supabase JWT token and returns user details.
    This ensures that the user is authenticated via Supabase.
    """
    token = auth.credentials
    try:
        # get_user() expects the access token
        user_response = supabase.auth.get_user(token)
        if not user_response or not user_response.user:
            raise HTTPException(status_code=401, detail="Invalid or expired session.")
        
        # User is verified
        return user_response.user
    except Exception as e:
        print(f"🔒 [AUTH-FAILURE] {str(e)}")
        raise HTTPException(status_code=401, detail="Authentication failed. Please log in again.")

def check_ownership(user_id: str, resource_owner_id: str):
    """
    Strict ownership verification to prevent IDOR vulnerabilities.
    """
    if user_id != resource_owner_id:
        raise HTTPException(status_code=403, detail="Unauthorized access to this resource.")
