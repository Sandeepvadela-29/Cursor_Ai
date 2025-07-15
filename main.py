"""
TrueFit Recruitment Platform - Main FastAPI Application
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
import time
import uvicorn
from loguru import logger

from app.core.config import settings
from app.core.database import create_tables
from app.api.v1.router import router as v1_router

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    TrueFit Recruitment Platform API - A comprehensive recruitment platform that finds the perfect match 
    between employers and employees based on comprehensive compatibility, not just skills and pay, 
    but also attitudes, worldviews, character, and cultural alignment.
    
    ## Features
    
    * **Authentication**: JWT-based authentication with email verification and MFA support
    * **User Management**: Separate candidate and employer profiles with comprehensive data
    * **Job Matching**: Advanced matching algorithm based on skills, culture, and values
    * **Communication**: Built-in messaging and interview scheduling
    * **Analytics**: Comprehensive analytics and reporting
    
    ## Getting Started
    
    1. Register as a candidate or employer
    2. Verify your email address
    3. Complete your profile
    4. Start matching!
    """,
    contact={
        "name": "TrueFit Support",
        "email": "support@truefit.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=settings.allowed_methods,
    allow_headers=settings.allowed_headers,
)

# Add trusted host middleware for security
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["localhost", "127.0.0.1", "*.truefit.com"]
)

# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Exception handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code
        }
    )

@app.exception_handler(500)
async def internal_server_error_handler(request: Request, exc: Exception):
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Internal server error",
            "status_code": 500
        }
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("Starting TrueFit Recruitment Platform API")
    # Create database tables
    try:
        create_tables()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down TrueFit Recruitment Platform API")

# Include API routes
app.include_router(v1_router, prefix=settings.api_v1_prefix)

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to TrueFit Recruitment Platform API",
        "version": settings.app_version,
        "docs": "/docs",
        "redoc": "/redoc",
        "health": f"{settings.api_v1_prefix}/health"
    }

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "TrueFit API is running",
        "version": settings.app_version
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        workers=1 if settings.debug else 4
    )