from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class InterviewEvaluation(Base):
    """面试评估模型"""
    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.id", ondelete="CASCADE"), index=True)
    evaluator_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), index=True)
    
    # 评分项
    overall_score = Column(Float, nullable=False)  # 综合评分
    technical_score = Column(Float, nullable=True)  # 技术能力评分
    communication_score = Column(Float, nullable=True)  # 沟通能力评分
    experience_score = Column(Float, nullable=True)  # 经验评分
    culture_fit_score = Column(Float, nullable=True)  # 文化匹配度评分
    
    # 评估结果
    result = Column(String(50), nullable=False)  # 评估结果，如：通过/不通过/待定
    conclusion = Column(Text, nullable=False)  # 评估结论
    
    # 候选人优缺点
    strengths = Column(JSON, nullable=True)  # 优势列表
    weaknesses = Column(JSON, nullable=True)  # 不足列表
    
    # 建议下一步
    next_step = Column(String(100), nullable=True)  # 下一步建议
    
    # 详细评价项
    technical_comments = Column(Text, nullable=True)  # 技术能力评价
    communication_comments = Column(Text, nullable=True)  # 沟通能力评价
    experience_comments = Column(Text, nullable=True)  # 经验评价
    cultural_comments = Column(Text, nullable=True)  # 文化匹配评价
    
    # 其他评价
    comments = Column(Text, nullable=True)  # 其他备注
    
    # 面试反馈汇总
    feedback_summary = Column(JSON, nullable=True)  # 所有面试官反馈的汇总
    
    # 元数据
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # 关系
    interview = relationship("Interview", back_populates="evaluation")
    evaluator = relationship(
        "User", 
        foreign_keys=[evaluator_id],
        backref="evaluations"
    )
    updater = relationship(
        "User", 
        foreign_keys=[updated_by],
        backref="updated_evaluations"
    ) 