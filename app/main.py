from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.db.mongodb import connect_to_mongodb, close_mongodb_connection
from app.db.influxdb import connect_to_influxdb, close_influxdb_connection

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events - startup and shutdown"""
    # Startup
    await connect_to_mongodb()
    connect_to_influxdb()
    yield
    # Shutdown
    await close_mongodb_connection()
    close_influxdb_connection()

# Create FastAPI app
app = FastAPI(
    title = settings.app_name,
    description = "API para seguimiento de finanzas personales",
    version = "1.0.0",
    lifespan = lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Personal Finance Tracker API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment": settings.env
    }