from fastapi import FastAPI
from api import tasks, auth
from database.db import create_table
from services.scheduler_service import SchedulerService
from services.notification_service import NotificationService

# Initialize FastAPI app
app = FastAPI(title="Todo App API", description="Event-driven TODO API with FastAPI")

# Initialize services as app state (to ensure they persist across the app lifecycle)
app.state.scheduler_service = None
app.state.notification_service = None

@app.on_event("startup")
async def startup_event():
    # Create database tables
    create_table()
    
    # Initialize and start services
    app.state.scheduler_service = SchedulerService()
    app.state.notification_service = NotificationService()
    
    app.state.scheduler_service.start()
    app.state.notification_service.start()
    
    print("All services started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    # Stop services if they were initialized
    if app.state.scheduler_service:
        app.state.scheduler_service.stop()
    if app.state.notification_service:
        app.state.notification_service.stop()
    print("All services stopped successfully")

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])

@app.get("/", tags=["Root"])
async def root():
    return {"message": "Welcome to the Todo App API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)