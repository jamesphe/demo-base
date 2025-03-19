from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.api_v1.api import api_router
from fastapi.exceptions import RequestValidationError
from app.api.errors import validation_exception_handler

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    # 允许的源列表，生产环境中应该设置为具体的域名
    allow_origins=[
        "http://localhost:9527",  # 开发环境前端地址
        "http://127.0.0.1:9527"
    ],
    allow_credentials=True,  # 允许携带凭证
    allow_methods=["*"],  # 允许的HTTP方法
    allow_headers=["*"],  # 允许的HTTP头
)

# 注册异常处理器
app.add_exception_handler(RequestValidationError, validation_exception_handler)

app.include_router(api_router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",  # 监听所有网络接口
        port=8000,
        reload=True
    ) 