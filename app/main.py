from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import auth, mall, camera, customer
from .database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(mall.router)
app.include_router(camera.router)
app.include_router(customer.router)

@app.get("/")
async def root():
    return {"message": "Welcome to the Mall Analytics API"}
