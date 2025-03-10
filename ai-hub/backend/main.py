from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from database import database, create_tables
from routers import credentials, tool

# Create FastAPI app
app = FastAPI(title="AI Account Pool Manager")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(credentials.router)
app.include_router(tool.router)

# Connect to database on startup
@app.on_event("startup")
async def startup():
    create_tables()
    await database.connect()
    print("Database connected")

# Disconnect from database on shutdown
@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
    print("Database disconnected")


# Run app directly when executing this file
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)