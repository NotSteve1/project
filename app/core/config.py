from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Project root
BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    # ============================================================
    # APPLICATION
    # ============================================================

    APP_NAME: str
    APP_VERSION: str
    DEBUG: bool
    ENVIRONMENT: str


    # ============================================================
    # DATABASE
    # ============================================================

    DATABASE_URL: str


    # ============================================================
    # JWT / AUTHENTICATION
    # ============================================================

    SECRET_KEY: str
    REFRESH_SECRET_KEY: str
    ALGORITHM: str

    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int


    # ============================================================
    # EMAIL
    # ============================================================

    MAIL_HOST: str
    MAIL_PORT: int
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM_ADDRESS: str
    MAIL_FROM_NAME: str

    MAIL_STARTTLS: bool
    MAIL_SSL_TLS: bool


    # ============================================================
    # MEDIA / FILE UPLOADS
    # ============================================================

    MEDIA_ROOT: Path
    MEDIA_URL: str

    MAX_PROFILE_IMAGE_SIZE: int

    ALLOWED_IMAGE_CONTENT_TYPES: set[str]

    MAX_VIDEO_SIZE_MB: int = 100
    MAX_TOTAL_STORAGE_MB: int = 9500
    B2_KEY_ID: str
    B2_APPLICATION_KEY: str
    B2_ENDPOINT: str
    B2_BUCKET_NAME: str 


    # ============================================================
    # PYDANTIC SETTINGS CONFIGURATION
    # ============================================================

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


# ================================================================
# GLOBAL SETTINGS INSTANCE
# ================================================================

settings = Settings()