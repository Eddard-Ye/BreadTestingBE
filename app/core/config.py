from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.schemas.auth import normalize_password


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    APP_NAME: str = "BreadTestingBE"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    JWT_SECRET_KEY: str = "bread-testing-dev-secret-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 10
    ADMIN_PASSWORD: str = "admin123"

    DATABASE_URL: str = (
        "mysql+pymysql://bread:bread123@127.0.0.1:3306/bread_testing?charset=utf8mb4"
    )

    SENSOR_CONFIG_PATH: str = "data/sensor_config.json"

    @property
    def database_url(self) -> str:
        return self.DATABASE_URL

    @field_validator("ADMIN_PASSWORD")
    @classmethod
    def normalize_admin_password(cls, value: str) -> str:
        return normalize_password(value)

    # 桌面应用（pywebview）
    DESKTOP_HOST: str = "127.0.0.1"
    DESKTOP_PORT: int = 8000
    DESKTOP_INIT_URL: str = "http://127.0.0.1:8000/static/desktop/index.html"
    DESKTOP_TITLE: str = ""
    DESKTOP_WIDTH: int = 1280
    DESKTOP_HEIGHT: int = 800
    DESKTOP_MIN_WIDTH: int = 1024
    DESKTOP_MIN_HEIGHT: int = 640
    DESKTOP_RESIZABLE: bool = False
    DESKTOP_GUI: str | None = None
    DESKTOP_FRAMELESS: bool = True
    DESKTOP_EASY_DRAG: bool = True
    DESKTOP_BACKGROUND_COLOR: str = "#020617"
    DESKTOP_DISABLE_TOUCH_SCROLL: bool = True
    DESKTOP_ZOOMABLE: bool = False


@lru_cache
def get_settings() -> Settings:
    return Settings()
