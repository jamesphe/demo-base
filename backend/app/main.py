from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.api_v1.api import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# 添加CORS中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:9527"],  # 允许的前端源
    allow_credentials=True,  # 允许携带cookie
    allow_methods=["*"],    # 允许的HTTP方法
    allow_headers=["*"],    # 允许的HTTP头
)

app.include_router(api_router, prefix=settings.API_V1_STR) 