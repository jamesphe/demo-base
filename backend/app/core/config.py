import secrets
from typing import List, Union
from pydantic import field_validator, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    
    # 将 CORS 配置改为字符串类型
    BACKEND_CORS_ORIGINS_STR: str = ""

    @computed_field
    @property
    def BACKEND_CORS_ORIGINS(self) -> List[str]:
        if not self.BACKEND_CORS_ORIGINS_STR:
            return []
        # 移除所有空格和引号
        v = self.BACKEND_CORS_ORIGINS_STR.replace(" ", "").replace("'", "").replace('"', "")
        # 移除方括号
        v = v.strip("[]")
        # 分割并过滤空字符串
        return [x.strip() for x in v.split(",") if x.strip()]

    PROJECT_NAME: str
    
    POSTGRES_SERVER: str
    POSTGRES_PORT: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    FIRST_SUPERUSER: str
    FIRST_SUPERUSER_PASSWORD: str

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return (
            f"postgresql://{self.POSTGRES_USER}:"
            f"{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:"
            f"{self.POSTGRES_PORT}/"
            f"{self.POSTGRES_DB}"
        )

    # 文件上传配置
    UPLOAD_DIR: str = "uploads"
    ALLOWED_EXTENSIONS: List[str] = ["pdf", "doc", "docx"]
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB

    # Celery配置
    REDIS_HOST: str
    REDIS_PORT: str
    REDIS_DB: str

    @computed_field
    @property
    def CELERY_BROKER_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    @computed_field
    @property
    def CELERY_RESULT_BACKEND(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    # 更新配置
    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        env_file_encoding='utf-8',
        extra='ignore'
    )


settings = Settings() 