"""
Main API v1 router
"""
from fastapi import APIRouter
from app.api.v1.auth import router as auth_router

# Create main v1 router
router = APIRouter(prefix="/v1")

# Include all route modules
router.include_router(auth_router)

# Health check endpoint
@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "TrueFit API is running"}