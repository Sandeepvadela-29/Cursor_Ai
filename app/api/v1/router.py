"""
Main API router for version 1.
Includes all endpoint routers with proper prefixes and tags.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, candidates, employers

# Create main API router
api_router = APIRouter()

# Include authentication routes
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"],
)

# Include user routes
api_router.include_router(
    users.router,
    prefix="/users",
    tags=["Users"],
)

# Include candidate routes
api_router.include_router(
    candidates.router,
    prefix="/candidates",
    tags=["Candidates"],
)

# Include employer routes
api_router.include_router(
    employers.router,
    prefix="/employers",
    tags=["Employers"],
)