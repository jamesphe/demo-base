import secrets
from typing import List, Union
from pydantic import field_validator, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
import os
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [x.strip() for x in v.split(",") if x.strip()]
        return v

    PROJECT_NAME: str = "蓝领用工平台"
    
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "blue_collar_platform")
    SQLALCHEMY_DATABASE_URI: str = ""  # 会在__init__中设置

    FIRST_SUPERUSER: str = "admin@example.com"
    FIRST_SUPERUSER_PASSWORD: str = "admin"
    USERS_OPEN_REGISTRATION: bool = False

    # Redis配置
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", "")

    # Celery配置
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

    # 文件上传配置
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
    MAX_CONTENT_LENGTH: int = int(os.getenv("MAX_CONTENT_LENGTH", "16777216"))  # 16MB

    # LLM配置
    LLM_API_TYPE: str = os.getenv("LLM_API_TYPE", "zhipu")
    LLM_API_BASE: str = os.getenv("LLM_API_BASE", "")
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_API_MODEL: str = os.getenv("LLM_API_MODEL", "glm-4")

    @computed_field
    def REDIS_URL(self) -> str:
        """构建Redis URL"""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    # 企业微信配置
    QYWX_PROVIDER_CORPID: str = os.getenv("QYWX_PROVIDER_CORPID", "")
    QYWX_PROVIDER_SECRET: str = os.getenv("QYWX_PROVIDER_SECRET", "")
    QYWX_SUITE_ID: str = os.getenv("QYWX_SUITE_ID", "")
    QYWX_SUITE_SECRET: str = os.getenv("QYWX_SUITE_SECRET", "")
    QYWX_SUITE_AGENT_ID: str = os.getenv("QYWX_SUITE_AGENT_ID", "")
    QYWX_TOKEN: str = os.getenv("QYWX_TOKEN", "")
    QYWX_ENCODING_AES_KEY: str = os.getenv("QYWX_ENCODING_AES_KEY", "")
    BASE_URL: str = os.getenv("BASE_URL", "https://your-domain.com")
    FRONTEND_BASE_URL: str = os.getenv("FRONTEND_BASE_URL", "http://localhost:9527")

    # 更新配置
    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def __init__(self, **data):
        super().__init__(**data)
        # 设置数据库连接URI
        self.SQLALCHEMY_DATABASE_URI = f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"


settings = Settings() 