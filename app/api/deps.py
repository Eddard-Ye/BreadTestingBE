from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.security import decode_access_token
from app.db.session import get_db
from app.services.measurement_service import MeasurementService, get_measurement_service
from app.services.recipe_service import RecipeService, get_recipe_service

bearer_scheme = HTTPBearer(auto_error=False)


def require_auth(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> str:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未登录",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        decode_access_token(settings, credentials.credentials)
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="登录已失效",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    return credentials.credentials


def get_recipe_service_dep(db: Session = Depends(get_db)) -> RecipeService:
    return get_recipe_service(db)


def get_measurement_service_dep(db: Session = Depends(get_db)) -> MeasurementService:
    return get_measurement_service(db)
