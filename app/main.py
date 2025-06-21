from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import auth, mall, camera, customer, analytics, id_management
from .database import engine, Base
from contextlib import asynccontextmanager
import asyncio
import logging
import socketio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Mall Analytics API...")
    
    # Start background tasks
    from .ai_solutions.websocket_manager import websocket_cleanup_task
    from .ai_solutions.socketio_server import socketio_analytics_broadcaster
    
    cleanup_task = asyncio.create_task(websocket_cleanup_task())
    socketio_task = asyncio.create_task(socketio_analytics_broadcaster())
    
    logger.info("Mall Analytics API started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Mall Analytics API...")
    
    # Stop background tasks
    cleanup_task.cancel()
    socketio_task.cancel()
    
    try:
        await cleanup_task
        await socketio_task
    except asyncio.CancelledError:
        pass
    
    # Stop all camera workers
    from .ai_solutions.camera_worker import camera_worker_manager
    await camera_worker_manager.stop_all_workers()
    
    logger.info("Mall Analytics API shutdown complete")

# Create FastAPI app
app = FastAPI(
    title="InsightCart Mall Analytics API",
    description="Advanced mall analytics system with real-time customer tracking and behavior analysis",
    version="2.0.0",
    lifespan=lifespan
)

# Import and mount Socket.io (simplified version)
from .ai_solutions.simple_socketio import get_socket_app
socket_app = get_socket_app(app)

# Configure CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001"  # Alternative port
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(mall.router)
app.include_router(camera.router)
app.include_router(customer.router)
app.include_router(analytics.router)  # New analytics routes
app.include_router(id_management.router)  # ID management routes

@app.get("/")
async def root():
    return {
        "message": "Welcome to InsightCart Mall Analytics API",
        "version": "2.0.0",
        "features": [
            "Real-time person detection and tracking",
            "Age and gender estimation",
            "Trolley detection and tracking",
            "Zone-based analytics",
            "Live WebSocket updates",
            "Comprehensive dashboard analytics"
        ],
        "status": "active"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": "2024-06-21T00:00:00Z",
        "services": {
            "database": "connected",
            "analytics_engine": "active",
            "websocket_manager": "active",
            "camera_workers": "ready"
        }
    }
