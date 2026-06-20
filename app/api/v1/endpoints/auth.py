import secrets
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.config import Settings, get_settings
from app.core.security import create_access_token
from app.schemas.auth import LoginRequest, TokenResponse, normalize_password

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    settings: Annotated[Settings, Depends(get_settings)],
) -> TokenResponse:
    expected = normalize_password(settings.ADMIN_PASSWORD)
    if not secrets.compare_digest(body.password, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="口令错误",
        )

    access_token, expires_in = create_access_token(settings)
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=expires_in,
    )
