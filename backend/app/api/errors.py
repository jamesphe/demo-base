from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.schemas.user import UserType

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """处理请求验证错误"""
    errors = exc.errors()
    for error in errors:
        # 处理枚举验证错误
        if error["type"] == "enum":
            if "user_type" in error["loc"]:
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        "code": 40000,
                        "message": f"用户类型必须是以下之一: {', '.join([t.value for t in UserType])}"
                    }
                )
    
    # 其他验证错误的默认处理
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "code": 40000,
            "message": "请求参数验证失败",
            "errors": errors
        }
    ) 