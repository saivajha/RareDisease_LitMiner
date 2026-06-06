from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from app.auth import (
    get_google_auth_url, exchange_code_for_token,
    get_google_user_info, is_allowed_domain, create_app_token, verify_token
)
from app.config import settings

router = APIRouter()


@router.get("/auth/login")
async def login():
    """Redirect to Google OAuth."""
    return RedirectResponse(url=get_google_auth_url())


@router.get("/auth/callback")
async def oauth_callback(code: str = None, error: str = None):
    """Handle Google OAuth callback."""
    if error or not code:
        return RedirectResponse(url=f"{settings.FRONTEND_URL}?auth_error=login_failed")
    try:
        token_data = await exchange_code_for_token(code)
        user_info = await get_google_user_info(token_data["access_token"])
        email = user_info.get("email", "")
        if not is_allowed_domain(email):
            return RedirectResponse(url=f"{settings.FRONTEND_URL}?auth_error=unauthorized_domain")
        app_token = create_app_token(
            email=email,
            name=user_info.get("name", ""),
            picture=user_info.get("picture", ""),
        )
        return RedirectResponse(url=f"{settings.FRONTEND_URL}?token={app_token}")
    except Exception as e:
        return RedirectResponse(url=f"{settings.FRONTEND_URL}?auth_error=login_failed")


@router.get("/auth/me")
async def get_me(user: dict = Depends(verify_token)):
    """Return the current authenticated user info."""
    return user
