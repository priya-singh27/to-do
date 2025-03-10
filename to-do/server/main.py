from fastapi import FastAPI
from contextlib import asynccontextmanager
from api import tasks, auth, user  
from database.db import create_table
from services.scheduler_service import SchedulerService
from services.notification_service import NotificationService
from fastapi.middleware.cors import CORSMiddleware
import os

# print(f'os.getenv("DATABASE_URL") ${os.getenv("DATABASE_URL")}')

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    create_table()  
    app.state.scheduler_service = SchedulerService()
    app.state.notification_service = NotificationService()

    app.state.scheduler_service.start()
    app.state.notification_service.start()
    print("All services started successfully")

    yield #this is where the app starts handling requests
    
    # Shutdown logic
    if app.state.scheduler_service:
        app.state.scheduler_service.stop()
    if app.state.notification_service:
        app.state.notification_service.stop()
    print("All services stopped successfully")

# Initialize FastAPI app with lifespan handler
app = FastAPI(
    title="Todo App API",
    description="Event-driven TODO API with FastAPI",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://23.94.253.229:5173","http://23.94.253.229", "http://localhost:5173", "http://localhost"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])
app.include_router(user.router, prefix="/users", tags=["Users"])

@app.get("/", tags=["Root"])
async def root():
    return {"message": "Welcome to the Todo App API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)