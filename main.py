from fastapi import FastAPI
from api import tasks, auth
from database.db import create_table
from contextlib import asynccontextmanager

# Initialize FastAPI app
app = FastAPI(title="Todo App API", description="Event-driven TODO API with FastAPI")

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])

@asynccontextmanager
async def startup_event():
    # Create database tables
    create_table()
    yield

@app.get("/", tags=["Root"])
async def root():
    return {"message": "Welcome to the Todo App API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)