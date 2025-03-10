from pydantic import BaseModel
from typing import Optional, List

class Tool(BaseModel):
    id: Optional[int] = None
    name: str
    auth_type: Optional[str] = "password"  # "password", "email_link", "api_key"
    description: Optional[str] = None

class ToolIn(BaseModel):
    name: str
    auth_type: Optional[str] = "password"
    description: Optional[str] = None

class CredentialRequest(BaseModel):
    tool_name: str