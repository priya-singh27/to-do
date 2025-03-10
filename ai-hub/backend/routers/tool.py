from fastapi import APIRouter, HTTPException, Request
from sqlalchemy.sql import select, update, func, desc
from datetime import datetime

from database import database, tools
from models.tool import Tool, ToolIn

router = APIRouter(prefix='/tool', tags=["ai_tools"])

@router.post('/add', response_model=Tool)
async def add_tool(tool: ToolIn):
    """Add a new AI tool"""
    query = tools.insert().values(
        name=tool.name,
        auth_type=tool.auth_type,
        description=tool.description
    )
    
    try:
        last_record_id = await database.execute(query)
    except Exception as e:
        if "UNIQUE constraint failed" in str(e):
            raise HTTPException(status_code=400, detail="Tool with this name already exists")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    return {
        "id": last_record_id,
        "name": tool.name,
        "auth_type": tool.auth_type,
        "description": tool.description
    }

@router.get('/all', response_model=list[Tool])
async def get_all_tools():
    """Get all registered AI tools"""
    query = select([tools])
    results = await database.fetch_all(query)
    return results

@router.get('/{tool_id}', response_model=Tool)
async def get_tool(tool_id: int):
    """Get a specific AI tool by ID"""
    query = select([tools]).where(tools.c.id == tool_id)
    result = await database.fetch_one(query)
    
    if not result:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    return result

@router.get('/name/{name}', response_model=Tool)
async def get_tool_by_name(name: str):
    """Get a specific AI tool by name"""
    query = select([tools]).where(tools.c.name == name)
    result = await database.fetch_one(query)
    
    if not result:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    return result

@router.put('/{tool_id}', response_model=Tool)
async def update_tool(tool_id: int, tool: ToolIn):
    """Update an existing AI tool"""
    query = select([tools]).where(tools.c.id == tool_id)
    existing_tool = await database.fetch_one(query)
    
    if not existing_tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    update_query = (
        tools.update()
        .where(tools.c.id == tool_id)
        .values(
            name=tool.name,
            auth_type=tool.auth_type,
            description=tool.description
        )
    )
    
    try:
        await database.execute(update_query)
    except Exception as e:
        if "UNIQUE constraint failed" in str(e):
            raise HTTPException(status_code=400, detail="Tool with this name already exists")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    return {
        "id": tool_id,
        "name": tool.name,
        "auth_type": tool.auth_type,
        "description": tool.description
    }

@router.delete('/{tool_id}')
async def delete_tool(tool_id: int):
    """Delete an AI tool"""
    query = select([tools]).where(tools.c.id == tool_id)
    existing_tool = await database.fetch_one(query)
    
    if not existing_tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    delete_query = tools.delete().where(tools.c.id == tool_id)
    await database.execute(delete_query)
    
    return {"detail": "Tool deleted successfully"}