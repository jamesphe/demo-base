from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, ConfigDict, Field


class InterviewEvaluationBase(BaseModel):
    """面试评估基础模型"""
    overall_score: float = Field(..., ge=1, le=5, description="综合评分")
    technical_score: Optional[float] = Field(None, ge=1, le=5, description="技术能力评分")
    communication_score: Optional[float] = Field(None, ge=1, le=5, description="沟通能力评分")
    experience_score: Optional[float] = Field(None, ge=1, le=5, description="经验评分")
    culture_fit_score: Optional[float] = Field(None, ge=1, le=5, description="文化匹配度评分")
    
    result: str = Field(..., description="评估结果，如：通过/不通过/待定")
    conclusion: str = Field(..., description="评估结论")
    
    strengths: Optional[List[str]] = Field(None, description="优势列表")
    weaknesses: Optional[List[str]] = Field(None, description="不足列表")
    
    next_step: Optional[str] = Field(None, description="下一步建议")
    
    # 其他详细评价项
    technical_comments: Optional[str] = Field(None, description="技术能力评价")
    communication_comments: Optional[str] = Field(None, description="沟通能力评价")
    experience_comments: Optional[str] = Field(None, description="经验评价")
    cultural_comments: Optional[str] = Field(None, description="文化匹配评价")
    
    # 其他字段
    comments: Optional[str] = Field(None, description="其他备注")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "overall_score": 4.0,
                "technical_score": 4.2,
                "communication_score": 3.8,
                "experience_score": 4.0,
                "culture_fit_score": 4.1,
                "result": "通过",
                "conclusion": "候选人整体表现良好，推荐进入下一轮面试",
                "strengths": ["技术基础扎实", "沟通清晰", "学习能力强"],
                "weaknesses": ["项目经验较少", "架构设计能力有待提高"],
                "next_step": "安排技术总监面试",
                "technical_comments": "基础知识扎实，编码能力强",
                "communication_comments": "表达清晰，思路流畅",
                "experience_comments": "有相关项目经验，但深度不够",
                "cultural_comments": "与团队文化相符",
                "comments": "候选人对加班态度积极，有较强的团队意识"
            }
        }
    )


class InterviewEvaluationCreate(InterviewEvaluationBase):
    """面试评估创建模型"""
    pass


class InterviewEvaluationUpdate(BaseModel):
    """面试评估更新模型"""
    overall_score: Optional[float] = Field(None, ge=1, le=5, description="综合评分")
    technical_score: Optional[float] = Field(None, ge=1, le=5, description="技术能力评分")
    communication_score: Optional[float] = Field(None, ge=1, le=5, description="沟通能力评分")
    experience_score: Optional[float] = Field(None, ge=1, le=5, description="经验评分")
    culture_fit_score: Optional[float] = Field(None, ge=1, le=5, description="文化匹配度评分")
    
    result: Optional[str] = Field(None, description="评估结果，如：通过/不通过/待定")
    conclusion: Optional[str] = Field(None, description="评估结论")
    
    strengths: Optional[List[str]] = Field(None, description="优势列表")
    weaknesses: Optional[List[str]] = Field(None, description="不足列表")
    
    next_step: Optional[str] = Field(None, description="下一步建议")
    
    # 其他详细评价项
    technical_comments: Optional[str] = Field(None, description="技术能力评价")
    communication_comments: Optional[str] = Field(None, description="沟通能力评价")
    experience_comments: Optional[str] = Field(None, description="经验评价")
    cultural_comments: Optional[str] = Field(None, description="文化匹配评价")
    
    # 其他字段
    comments: Optional[str] = Field(None, description="其他备注")


class InterviewEvaluationResponse(InterviewEvaluationBase):
    """面试评估响应模型"""
    id: int
    interview_id: int
    evaluator_id: int
    evaluator_name: Optional[str] = None
    feedback_summary: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


# 下一步操作的可能选项
class NextStepOption(BaseModel):
    """下一步操作选项"""
    action: str = Field(..., description="操作类型")
    label: str = Field(..., description="选项显示名称")
    description: str = Field(..., description="选项描述")
    
    # 操作相关参数
    params: Optional[Dict[str, Any]] = Field(None, description="操作参数")
    
    # UI显示相关
    icon: Optional[str] = Field(None, description="图标")
    type: Optional[str] = Field(None, description="样式类型") 