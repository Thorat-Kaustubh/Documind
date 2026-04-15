import os
import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client, Client
from dotenv import load_dotenv
from database.postgres_sync import PostgresSync

load_dotenv()
logger = logging.getLogger("documind.auth")
db = PostgresSync()

class UserSession(BaseModel):
    """
    SECTION 6: CENTRALIZED USER SESSION
    Hardened Identity + Role-Based Access Tracking.
    """
    id: str
    email: Optional[str] = None
    profile: Dict[str, Any] = {}
    tier: str = "FREE" # FREE, PRO, ELITE
    permissions: List[str] = []

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_anon_key = os.getenv("SUPABASE_ANON_KEY")
supabase: Client = create_client(supabase_url, supabase_anon_key) if supabase_url and supabase_anon_key else None

security = HTTPBearer()

async def get_current_user(auth: HTTPAuthorizationCredentials = Depends(security)) -> UserSession:
    """
    SECTION 6.2: CENTRALIZED JWT VERIFICATION
    Aegis Security Layer for FastAPI.
    """
    token = auth.credentials
    try:
        if not supabase:
            raise HTTPException(status_code=500, detail="AUTH_SERVICE_UNAVAILABLE")
        
        # 1. VERIFY JWT (Supabase Identity)
        user_response = supabase.auth.get_user(token)
        if not user_response or not user_response.user:
            raise HTTPException(status_code=401, detail="INVALID_SESSION")
        
        user = user_response.user
        
        # 2. FETCH ROLE & PERMISSIONS (Direct DB Access)
        # This ensures real-time tier updates are respected
        profile = db.get_user_profile(user.id)
        
        if not profile:
             # Emergency Sync
             logger.warning(f"Profile missing for {user.id}. Attempting rapid sync.")
             profile = db.ensure_profile_exists(user.id, user.email)
        
        tier = profile.get("tier", "FREE") if profile else "FREE"
        
        # RBAC Mapping
        permissions = ["chat", "basic_research"]
        if tier in ["PRO", "ELITE"]:
            permissions += ["expert_analysis", "historical_data", "pdf_extraction"]
        if tier == "ELITE":
            permissions += ["real_time_signals", "priority_execution"]

        return UserSession(
            id=user.id,
            email=user.email,
            profile=dict(profile) if profile else {},
            tier=tier,
            permissions=permissions
        )
        
    except Exception as e:
        logger.error(f"Security Alert: {str(e)}")
        raise HTTPException(status_code=401, detail="Authentication failed.")

def require_tier(required_tier: str):
    """
    Decorator-style dependency for Role-Based Access.
    """
    tiers = ["FREE", "PRO", "ELITE"]
    req_index = tiers.index(required_tier)
    
    async def tier_checker(user: UserSession = Depends(get_current_user)):
        user_index = tiers.index(user.tier)
        if user_index < req_index:
            raise HTTPException(
                status_code=403, 
                detail=f"Tier Upgrade Required. This feature is restricted to {required_tier} users."
            )
        return user
        
    return tier_checker
