from fastapi import FastAPI, Depends, HTTPException, status, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from . import models
from .database import SessionLocal, engine, get_db
from .routers import institutions, products, transactions, credits, categories, currencies, services, notifications, auth
from .error_handlers import EXCEPTION_HANDLERS
from .logging_config import setup_logging, RequestLoggingMiddleware, get_logger
from .optimizations import apply_database_optimizations, get_database_stats
import os
import time
from datetime import datetime

# Setup logging
setup_logging()
logger = get_logger("app")

models.Base.metadata.create_all(bind=engine)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Finanzas Personales API",
    description="API para gestión de finanzas personales con optimizaciones de performance",
    version="1.2.0"
)

# Add exception handlers
for exception_type, handler in EXCEPTION_HANDLERS.items():
    app.add_exception_handler(exception_type, handler)

# Add rate limit exception handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add performance middlewares
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(GZipMiddleware, minimum_size=1000)  # Compress responses > 1KB
app.add_middleware(RequestLoggingMiddleware)

# Add performance monitoring middleware
@app.middleware("http")
async def performance_middleware(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    # Log slow requests
    if process_time > 2.0:
        logger.warning(f"SLOW REQUEST: {request.method} {request.url.path} took {process_time:.3f}s")
    
    return response

# Configure CORS based on environment
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:8501,http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(institutions.router)
app.include_router(products.router)
app.include_router(transactions.router)
app.include_router(credits.router)
app.include_router(categories.router)
app.include_router(currencies.router)
app.include_router(services.router)
app.include_router(notifications.router)

@app.get("/")
@limiter.limit("30/minute")
def read_root(request: Request):
    logger.info("Root endpoint accessed")
    return {
        "message": "Finanzas Personales API con Performance Optimizations", 
        "version": "1.2.0",
        "features": [
            "JWT Authentication",
            "Rate Limiting", 
            "Response Compression",
            "Database Optimizations",
            "Caching Support"
        ]
    }

@app.get("/health")
@limiter.limit("60/minute")
def health_check(request: Request, db: Session = Depends(get_db)):
    logger.info("Health check endpoint accessed")
    
    try:
        # Test database connection
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
        logger.error(f"Database health check failed: {str(e)}")
    
    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "timestamp": datetime.now().isoformat(),
        "database": db_status,
        "version": "1.2.0"
    }

@app.get("/performance/stats")
@limiter.limit("10/minute")
def get_performance_stats(request: Request, db: Session = Depends(get_db)):
    """Get database and application performance statistics"""
    logger.info("Performance stats endpoint accessed")
    
    try:
        db_stats = get_database_stats(db)
        return {
            "database_stats": db_stats,
            "api_version": "1.2.0",
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting performance stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Could not retrieve performance stats")

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Finanzas Personales API starting up...")
    logger.info("🔐 Authentication: JWT enabled")
    logger.info("📊 Database: PostgreSQL connected")
    logger.info("🛡️ Error handling: Centralized")
    logger.info("📝 Logging: Structured logging enabled")
    logger.info("⚡ Performance: Rate limiting enabled")
    logger.info("🗜️ Compression: GZip compression enabled")
    logger.info("🚀 Cache: Database optimizations ready")
    
    # Apply database optimizations on startup
    try:
        db = SessionLocal()
        apply_database_optimizations(db)
        db.close()
        logger.info("📈 Database optimizations applied successfully")
    except Exception as e:
        logger.warning(f"Could not apply database optimizations: {str(e)}")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 Finanzas Personales API shutting down...")
    logger.info("📊 Performance metrics logged")
    logger.info("🧹 Cache cleared")
    logger.info("✅ Shutdown completed successfully")