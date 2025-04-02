from typing import Any, Dict, Optional, Generic, TypeVar, List
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

T = TypeVar('T')

class Meta(BaseModel):
    """分页元数据"""
    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    per_page: int = Field(..., description="每页记录数")
    total_pages: int = Field(..., description="总页数")

class ListResponse(BaseModel, Generic[T]):
    """通用列表响应格式"""
    data: List[T]
    meta: Meta