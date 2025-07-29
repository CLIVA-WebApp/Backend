from fastapi import APIRouter, Depends, Query
from fastapi.responses import RedirectResponse
from src.config.settings import settings
from src.controllers.auth_controller import auth_controller
from src.models.user import User
from src.middleware.auth_middleware import get_current_user_required
from src.schemas.auth_schema import (
    GoogleAuthRequest, 
    GoogleAuthResponse, 
    AuthURLResponse,
    UserResponse
)

# Create router with prefix and tags
auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

@auth_router.get("/google", summary="Redirect to Google OAuth")
async def redirect_to_google():
    url = await auth_controller.get_google_auth_url()
    return RedirectResponse(url.auth_url)


@auth_router.get("/google/callback", summary="OAuth Callback")
async def google_callback(code: str = Query(...), state: str = Query(...)):
    jwt = await auth_controller.google_callback(code, state)

    return RedirectResponse(f"{settings.frontend_url}/auth/success?token={jwt.access_token}")


@auth_router.get(
    "/me", 
    response_model=UserResponse,
    summary="Get Current User",
    description="Get current authenticated user profile information"
)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user_required)
) -> UserResponse:
    return await auth_controller.get_current_user_profile(current_user)

@auth_router.post(
    "/logout",
    summary="Logout User",
    description="Logout current authenticated user"
)
async def logout(
    current_user: User = Depends(get_current_user_required)
) -> dict:
    return await auth_controller.logout(current_user)