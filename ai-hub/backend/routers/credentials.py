from fastapi import APIRouter, HTTPException, Request
from sqlalchemy.sql import select, update, func, desc
from datetime import datetime, timedelta

from database import database, credentials, tools, usage_logs, auth_sessions
from models.credentials import Credential, CredentialIn, CredentialOut
from models.tool import CredentialRequest
from models.usagelog import UsageLog, CredentialStatus, AuthSessionIn, AuthSession

router = APIRouter(prefix='/credential', tags=["credentials"])

@router.post('/add', response_model=Credential)
async def add_credential(credential: CredentialIn):
    """Add a new credential to the pool"""
    query = credentials.insert().values(
        email=credential.email,
        password=credential.password,
        is_available=True,
        cooldown_minutes=credential.cooldown_minutes
    )
    
    try:
        last_record_id = await database.execute(query)
    except Exception as e:
        if "UNIQUE constraint failed" in str(e):
            raise HTTPException(status_code=400, detail="Credential with this email already exists")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    return {
        "id": last_record_id,
        "email": credential.email,
        "password": credential.password,
        "is_available": True,
        "cooldown_minutes": credential.cooldown_minutes
    }

@router.post('/get', response_model=CredentialOut)
async def get_credential(request: CredentialRequest, req: Request):
    """Get an available credential for the specified tool"""
    now = datetime.now().timestamp()
    
    # First, verify the tool exists
    tool_query = select([tools]).where(tools.c.name == request.tool_name)
    tool = await database.fetch_one(tool_query)
    
    if not tool:
        raise HTTPException(status_code=404, detail=f"Tool '{request.tool_name}' not found")
    
    # Check when credentials were last used
    last_usage_subquery = (
        select([
            usage_logs.c.credential_id,
            func.max(usage_logs.c.timestamp).label("last_used")
        ])
        .group_by(usage_logs.c.credential_id)
        .alias("last_usage")
    )
    
    # Find available credentials
    query = (
        select([
            credentials.c.id,
            credentials.c.email,
            credentials.c.password,
            credentials.c.cooldown_minutes,
            credentials.c.is_available,
            last_usage_subquery.c.last_used
        ])
        .select_from(
            credentials.outerjoin(
                last_usage_subquery,
                credentials.c.id == last_usage_subquery.c.credential_id
            )
        )
        .where(
            (credentials.c.is_available == True) |
            (last_usage_subquery.c.last_used == None) |
            (now - last_usage_subquery.c.last_used > credentials.c.cooldown_minutes * 60)
        )
    )
    
    available_credentials = await database.fetch_all(query)
    
    if not available_credentials:
        raise HTTPException(status_code=503, detail="No available credentials")
    
    # Choose a credential with fewer recent usages
    chosen_credential = available_credentials[0]
    
    # Update credential status
    update_query = (
        credentials.update()
        .where(credentials.c.id == chosen_credential["id"])
        .values(is_available=False)
    )
    
    await database.execute(update_query)
    
    # Log the usage
    log_query = usage_logs.insert().values(
        credential_id=chosen_credential["id"],
        tool_id=tool["id"],
        timestamp=now
    )
    
    await database.execute(log_query)
    
    # Check if there's a valid session for this credential and tool
    session_query = (
        select([auth_sessions])
        .where(
            (auth_sessions.c.credential_id == chosen_credential["id"]) &
            (auth_sessions.c.tool_id == tool["id"]) &
            (auth_sessions.c.is_valid == True) &
            (auth_sessions.c.expires_at > now)
        )
        .order_by(desc(auth_sessions.c.created_at))
        .limit(1)
    )
    
    session = await database.fetch_one(session_query)
    
    # Return credentials and session data if available
    response = {
        "id": chosen_credential["id"],
        "email": chosen_credential["email"],
        "password": chosen_credential["password"],
        "tool": {
            "id": tool["id"],
            "name": tool["name"],
            "auth_type": tool["auth_type"]
        }
    }
    
    if session:
        response["session_data"] = session["session_data"]
    
    return response

@router.post('/release', response_model=dict)
async def release_credential(log: UsageLog):
    """Release a credential after use"""
    now = datetime.now().timestamp()
    
    # Get credential info
    query = select([credentials]).where(credentials.c.id == log.credential_id)
    credential = await database.fetch_one(query)
    
    if not credential:
        raise HTTPException(status_code=404, detail="Credential not found")
    
    # Find the most recent usage log for this credential
    usage_query = (
        select([usage_logs])
        .where(usage_logs.c.credential_id == log.credential_id)
        .order_by(desc(usage_logs.c.timestamp))
        .limit(1)
    )
    
    last_usage = await database.fetch_one(usage_query)
    
    if last_usage:
        # Update the session duration if we found a matching log
        duration = int(now - last_usage["timestamp"])
        
        update_duration_query = (
            usage_logs.update()
            .where(usage_logs.c.id == last_usage["id"])
            .values(session_duration=duration)
        )
        
        await database.execute(update_duration_query)
    
    # Mark credential as available again
    update_query = (
        credentials.update()
        .where(credentials.c.id == log.credential_id)
        .values(is_available=True)
    )
    
    await database.execute(update_query)
    
    return {"status": "success", "message": "Credential released"}

@router.get('/status', response_model=list[CredentialStatus])
async def get_credential_status():
    """Get status overview of all credentials"""
    now = datetime.now().timestamp()
    
    # Get last usage time and tool for each credential
    last_usage_subquery = (
        select([
            usage_logs.c.credential_id,
            func.max(usage_logs.c.timestamp).label("last_used"),
            usage_logs.c.tool_id
        ])
        .group_by(usage_logs.c.credential_id)
        .alias("last_usage")
    )
    
    # Count total usages for each credential
    usage_count_subquery = (
        select([
            usage_logs.c.credential_id,
            func.count().label("usage_count")
        ])
        .group_by(usage_logs.c.credential_id)
        .alias("usage_count")
    )
    
    # Join everything together
    query = (
        select([
            credentials.c.id,
            credentials.c.email,
            credentials.c.is_available,
            credentials.c.cooldown_minutes,
            last_usage_subquery.c.last_used,
            last_usage_subquery.c.tool_id,
            usage_count_subquery.c.usage_count,
            tools.c.name.label("tool_name")
        ])
        .select_from(
            credentials
            .outerjoin(last_usage_subquery, credentials.c.id == last_usage_subquery.c.credential_id)
            .outerjoin(usage_count_subquery, credentials.c.id == usage_count_subquery.c.credential_id)
            .outerjoin(tools, last_usage_subquery.c.tool_id == tools.c.id)
        )
    )
    
    results = await database.fetch_all(query)
    
    credentials_status = []
    
    for cred in results:
        cooldown_end = (cred["last_used"] or 0) + cred["cooldown_minutes"] * 60
        time_until_available = max(0, cooldown_end - now)
        
        credentials_status.append({
            "id": cred["id"],
            "email": cred["email"],
            "is_available": cred["is_available"] or time_until_available <= 0,
            "last_used": datetime.fromtimestamp(cred["last_used"]).isoformat() if cred["last_used"] else None,
            "last_tool": cred["tool_name"],
            "usage_count": cred["usage_count"] or 0,
            "seconds_until_available": int(time_until_available)
        })
    
    return credentials_status

@router.get('/all', response_model=list[Credential])
async def get_all_credentials():
    """Get all credentials"""
    query = select([credentials])
    results = await database.fetch_all(query)
    return results

@router.post('/session/add', response_model=AuthSession)
async def add_auth_session(session: AuthSessionIn):
    """Add a new authentication session"""
    now = datetime.now().timestamp()
    
    # Verify the tool exists
    tool_query = select([tools]).where(tools.c.name == session.tool_name)
    tool = await database.fetch_one(tool_query)
    
    if not tool:
        raise HTTPException(status_code=404, detail=f"Tool '{session.tool_name}' not found")
    
    # Verify the credential exists
    cred_query = select([credentials]).where(credentials.c.id == session.credential_id)
    cred = await database.fetch_one(cred_query)
    
    if not cred:
        raise HTTPException(status_code=404, detail="Credential not found")
    
    # Calculate expiry timestamp
    expires_at = now + (session.expires_days * 24 * 60 * 60)
    
    # Invalidate previous sessions for this credential and tool
    invalidate_query = (
        auth_sessions.update()
        .where(
            (auth_sessions.c.credential_id == session.credential_id) &
            (auth_sessions.c.tool_id == tool["id"])
        )
        .values(is_valid=False)
    )
    
    await database.execute(invalidate_query)
    
    # Insert new session
    query = auth_sessions.insert().values(
        tool_id=tool["id"],
        credential_id=session.credential_id,
        session_data=session.session_data,
        created_at=now,
        expires_at=expires_at,
        is_valid=True
    )
    
    session_id = await database.execute(query)
    
    return {
        "id": session_id,
        "tool_id": tool["id"],
        "credential_id": session.credential_id,
        "session_data": session.session_data,
        "created_at": now,
        "expires_at": expires_at,
        "is_valid": True
    }

@router.get('/session/status', response_model=list)
async def get_auth_session_status():
    """Get status of all authentication sessions"""
    now = datetime.now().timestamp()
    
    query = (
        select([
            auth_sessions.c.id,
            auth_sessions.c.credential_id,
            auth_sessions.c.tool_id,
            auth_sessions.c.created_at,
            auth_sessions.c.expires_at,
            auth_sessions.c.is_valid,
            tools.c.name.label("tool_name"),
            credentials.c.email
        ])
        .select_from(
            auth_sessions
            .join(tools, auth_sessions.c.tool_id == tools.c.id)
            .join(credentials, auth_sessions.c.credential_id == credentials.c.id)
        )
        .order_by(desc(auth_sessions.c.created_at))
    )
    
    results = await database.fetch_all(query)
    
    sessions = []
    for s in results:
        days_until_expiry = (s["expires_at"] - now) / (24 * 60 * 60)
        is_expired = s["expires_at"] < now
        
        sessions.append({
            "id": s["id"],
            "credential_email": s["email"],
            "tool_name": s["tool_name"],
            "created_at": datetime.fromtimestamp(s["created_at"]).isoformat(),
            "expires_at": datetime.fromtimestamp(s["expires_at"]).isoformat(),
            "days_until_expiry": round(max(0, days_until_expiry), 1),
            "is_valid": s["is_valid"],
            "is_expired": is_expired
        })
    
    return sessions

@router.post('/session/invalidate/{session_id}')
async def invalidate_session(session_id: int):
    """Invalidate an authentication session"""
    query = select([auth_sessions]).where(auth_sessions.c.id == session_id)
    session = await database.fetch_one(query)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    update_query = (
        auth_sessions.update()
        .where(auth_sessions.c.id == session_id)
        .values(is_valid=False)
    )
    
    await database.execute(update_query)
    
    return {"status": "success", "message": "Session invalidated"}