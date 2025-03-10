from pydantic import BaseModel
from typing import Optional, Dict, Any

class Credential(BaseModel):
    id: Optional[int] = None
    email: str
    password: str
    is_available: Optional[bool] = True
    cooldown_minutes: Optional[int] = 10

class CredentialIn(BaseModel):
    email: str
    password: str
    cooldown_minutes: Optional[int] = 10

class CredentialOut(BaseModel):
    id: int
    email: str
    password: str
    tool: Dict[str, Any]  # Tool information
    session_data: Optional[str] = None  # For email-link based auth