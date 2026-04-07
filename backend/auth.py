import os
import logging
from typing import Dict, Any, Optional
from pydantic import BaseModel
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("documind.auth")

class UserSession(BaseModel):
    """Consolidated Research Session: Identity + Public Profile."""
    id: str
    email: Optional[str] = None
    profile: Dict[str, Any] = {}

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_anon_key = os.getenv("SUPABASE_ANON_KEY")
supabase: Client = create_client(supabase_url, supabase_anon_key) if supabase_url and supabase_anon_key else None

security = HTTPBearer()

async def get_current_user(auth: HTTPAuthorizationCredentials = Depends(security)) -> UserSession:
    """
    Verifies the Supabase JWT token and returns consolidated user + profile details.
    This ensures the user is authenticated AND their custom research profile is loaded.
    """
    token = auth.credentials
    try:
        if not supabase:
            raise HTTPException(status_code=500, detail="Supabase client not initialized. Check backend .env")
        
        # 1. VERIFY IDENTITY (Supabase JWT)
        user_response = supabase.auth.get_user(token)
        if not user_response or not user_response.user:
            raise HTTPException(status_code=401, detail="Invalid session.")
        
        user = user_response.user
        
        # 2. FETCH PUBLIC PROFILE (Tier, metadata, preferences)
        profile_res = supabase.table("profiles").select("*").eq("id", user.id).execute()
        profile = profile_res.data[0] if profile_res.data else {}
        
        return UserSession(
            id=user.id,
            email=user.email,
            profile=profile
        )
    except Exception as e:
        logger.error(f"🔒 [AUTH-FAILURE] {str(e)}")
        raise HTTPException(status_code=401, detail="Authentication failed. Please log in again.")

def check_ownership(user_id: str, resource_owner_id: str):
    """Strict ownership verification to prevent IDOR vulnerabilities."""
    if user_id != resource_owner_id:
        raise HTTPException(status_code=403, detail="Unauthorized access to this resource.")
