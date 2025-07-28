from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register")
async def register():
    """Register new user"""
    return {"message": "Register endpoint"}

@router.post("/login")
async def login():
    """Login user"""
    return {"message": "Login endpoint"}

@router.post("/logout")
async def logout():
    """Logout user"""
    return {"message": "Logout endpoint"} 