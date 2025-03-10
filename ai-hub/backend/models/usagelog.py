from pydantic import BaseModel
from typing import Optional, List

class UsageLog(BaseModel):
    credential_id: int
    tool_id: Optional[int] = None

class UsageRecord(BaseModel):
    id: int
    tool_name: str
    timestamp: str
    session_duration: Optional[int] = None

class CredentialStatus(BaseModel):
    id: int
    email: str
    is_available: bool
    last_used: Optional[str] = None
    last_tool: Optional[str] = None
    usage_count: int
    seconds_until_available: int

class AuthSession(BaseModel):
    id: Optional[int] = None
    tool_id: int
    credential_id: int
    session_data: str
    created_at: float
    expires_at: float
    is_valid: bool = True

class AuthSessionIn(BaseModel):
    tool_name: str
    credential_id: int
    session_data: str
    expires_days: Optional[int] = 30  # Default expiry in days