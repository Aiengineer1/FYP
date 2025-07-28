from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .routes import auth, mall, camera, customer, analytics, id_management
from .ai_solutions.communication.websocket_manager import websocket_cleanup_task
from .ai_solutions.communication.socketio_server import socketio_analytics_broadcaster
from .ai_solutions.camera_worker import camera_worker_manager
from .ai_solutions.communication.simple_socketio import get_socket_app
import logging
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Mall Analytics API...")
    
    # Start background tasks
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
    try:
        camera_worker_manager.stop_all_cameras()
    except Exception as e:
        logger.error(f"Error stopping camera workers: {e}")

# Create FastAPI app
app = FastAPI(
    title="Mall Analytics API",
    description="Real-time mall analytics and customer tracking system",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(mall.router, tags=["mall"])
app.include_router(camera.router)
app.include_router(customer.router, tags=["customer"])
app.include_router(analytics.router, tags=["analytics"])
app.include_router(id_management.router, tags=["id-management"])

# Mount Socket.IO app
socketio_app = get_socket_app()
app.mount("/socket.io", socketio_app)

@app.get("/")
async def root():
    return {"message": "Mall Analytics API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is operational"}
