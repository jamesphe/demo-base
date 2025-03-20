from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class ResponseMsg(BaseModel):
    """通用响应消息模型"""
    message: str = Field(..., description="响应消息")
    data: Optional[Dict[str, Any]] = Field(None, description="响应数据")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "操作成功",
                "data": None
            }
        }


class ResumeParseResponse(BaseModel):
    """简历解析响应模型"""
    parsed_data: Dict[str, Any] = Field(..., description="解析结果")
    
    class Config:
        json_schema_extra = {
            "example": {
                "parsed_data": {
                    "name": "张三",
                    "phone": "13800138000",
                    "skills": ["Python", "数据分析"]
                }
            }
        }