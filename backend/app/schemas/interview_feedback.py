from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, ConfigDict, Field


class TechnicalEvaluation(BaseModel):
    """技术能力评估项"""
    coding_ability: Optional[float] = Field(None, ge=1, le=5, description="编码能力评分")
    problem_solving: Optional[float] = Field(None, ge=1, le=5, description="解决问题能力评分")
    system_design: Optional[float] = Field(None, ge=1, le=5, description="系统设计能力评分")
    algorithm: Optional[float] = Field(None, ge=1, le=5, description="算法能力评分")
    knowledge_depth: Optional[float] = Field(None, ge=1, le=5, description="知识深度评分")
    knowledge_breadth: Optional[float] = Field(None, ge=1, le=5, description="知识广度评分")
    comments: Optional[Dict[str, str]] = Field(None, description="各项能力的详细评语")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "coding_ability": 4.5,
                "problem_solving": 4.0,
                "system_design": 3.5,
                "algorithm": 4.0,
                "knowledge_depth": 4.0,
                "knowledge_breadth": 3.5,
                "comments": {
                    "coding_ability": "代码结构清晰，命名规范",
                    "problem_solving": "能够快速理解问题并提供解决方案",
                    "system_design": "系统设计合理，但缺乏细节考虑",
                    "algorithm": "对常见算法理解深入",
                    "knowledge_depth": "在主要技术栈上有扎实基础",
                    "knowledge_breadth": "技术栈较为单一"
                }
            }
        }
    )


class ComprehensiveEvaluation(BaseModel):
    """综合素质评估项"""
    communication: Optional[float] = Field(None, ge=1, le=5, description="沟通能力评分")
    teamwork: Optional[float] = Field(None, ge=1, le=5, description="团队协作能力评分")
    learning_ability: Optional[float] = Field(None, ge=1, le=5, description="学习能力评分")
    pressure_handling: Optional[float] = Field(None, ge=1, le=5, description="抗压能力评分")
    cultural_fit: Optional[float] = Field(None, ge=1, le=5, description="文化匹配度评分")
    comments: Optional[Dict[str, str]] = Field(None, description="各项能力的详细评语")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "communication": 4.0,
                "teamwork": 4.5,
                "learning_ability": 4.0,
                "pressure_handling": 3.5,
                "cultural_fit": 4.0,
                "comments": {
                    "communication": "表达清晰，思路流畅",
                    "teamwork": "有丰富的团队协作经验",
                    "learning_ability": "学习能力强，乐于接受新知识",
                    "pressure_handling": "在压力下能保持冷静，但偶有紧张",
                    "cultural_fit": "价值观与公司文化高度一致"
                }
            }
        }
    )


class HiringRecommendation(str):
    """录用建议枚举"""
    STRONG_RECOMMEND = "strong_recommend"
    RECOMMEND = "recommend"
    NEUTRAL = "neutral"
    NOT_RECOMMEND = "not_recommend"
    STRONG_NOT_RECOMMEND = "strong_not_recommend"


class InterviewerFeedbackBase(BaseModel):
    """面试官反馈基础模型"""
    feedback: Optional[str] = None
    evaluation_score: Optional[float] = Field(None, ge=1, le=5, description="总体评分")
    technical_evaluation: Optional[TechnicalEvaluation] = None
    comprehensive_evaluation: Optional[ComprehensiveEvaluation] = None
    strengths: Optional[str] = None
    weaknesses: Optional[str] = None
    hiring_recommendation: Optional[str] = None
    preparation_notes: Optional[str] = None
    process_record: Optional[str] = Field(None, description="面试过程记录")


class InterviewerFeedbackCreate(InterviewerFeedbackBase):
    """创建面试官反馈"""
    interview_id: int
    interviewer_id: int


class InterviewerFeedbackUpdate(InterviewerFeedbackBase):
    """更新面试官反馈"""
    pass


class InterviewerFeedback(InterviewerFeedbackBase):
    """面试官反馈完整模型"""
    interview_id: int
    interviewer_id: int
    status: str
    created_at: datetime
    updated_at: datetime
    
    # 添加面试官信息
    interviewer_name: Optional[str] = None
    interviewer_title: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class InterviewFeedbackSummary(BaseModel):
    """面试反馈汇总"""
    interview_id: int
    average_score: float
    interviewer_count: int
    completed_count: int
    recommendation_summary: Dict[str, int]
    
    # 所有面试官的评分详情
    feedbacks: List[InterviewerFeedback]
    
    # 统计性数据
    technical_averages: Dict[str, float]
    comprehensive_averages: Dict[str, float]
    
    # 候选人优缺点汇总
    key_strengths: List[str]
    key_weaknesses: List[str]
    
    model_config = ConfigDict(from_attributes=True) 