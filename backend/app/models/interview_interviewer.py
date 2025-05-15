from sqlalchemy import Column, Integer, ForeignKey, Table, String, Text, Float, DateTime, JSON
from app.db.base_class import Base

# 定义面试与面试官的多对多关系表
interview_interviewers = Table(
    "interview_interviewers",
    Base.metadata,
    Column(
        "interview_id", 
        Integer, 
        ForeignKey("interviews.id", ondelete="CASCADE"), 
        primary_key=True
    ),
    Column(
        "interviewer_id", 
        Integer, 
        ForeignKey("users.id", ondelete="CASCADE"), 
        primary_key=True
    ),
    Column("feedback", Text),  # 面试官对此次面试的反馈
    Column("evaluation_score", Float),  # 面试官评分
    Column("status", String(50), default="pending"),  # 面试官状态
    Column("technical_evaluation", JSON),  # 技术评估详情
    Column("comprehensive_evaluation", JSON),  # 综合素质评估
    Column("strengths", Text),  # 候选人优势
    Column("weaknesses", Text),  # 候选人劣势
    Column("hiring_recommendation", String(50)),  # 录用建议
    Column("preparation_notes", Text),  # 面试准备材料(Markdown格式)
    Column("process_record", Text),  # 面试过程记录
    Column("created_at", DateTime),
    Column("updated_at", DateTime)
) 