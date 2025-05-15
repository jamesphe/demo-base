from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
import statistics
from collections import Counter
from fastapi import HTTPException

from app import models
from app.schemas.interview_feedback import (
    InterviewerFeedbackCreate,
    InterviewerFeedbackUpdate,
    InterviewFeedbackSummary
)


class InterviewFeedbackService:
    def create_feedback(
        self,
        db: Session,
        feedback_in: InterviewerFeedbackCreate
    ) -> Dict[str, Any]:
        """创建面试官反馈"""
        # 检查是否已存在反馈
        existing = self.get_interviewer_feedback(
            db=db,
            interview_id=feedback_in.interview_id,
            interviewer_id=feedback_in.interviewer_id
        )
        
        if existing:
            # 如果已存在，则更新
            return self.update_feedback(
                db=db,
                interview_id=feedback_in.interview_id,
                interviewer_id=feedback_in.interviewer_id,
                feedback_in=feedback_in
            )
        
        # 更新interview_interviewers表中的记录
        query = db.query(models.interview_interviewers).filter(
            models.interview_interviewers.c.interview_id == (
                feedback_in.interview_id
            ),
            models.interview_interviewers.c.interviewer_id == (
                feedback_in.interviewer_id
            )
        )
        
        # 准备技术评估数据
        tech_eval = None
        if feedback_in.technical_evaluation:
            tech_eval = feedback_in.technical_evaluation.dict()
        
        # 准备综合评估数据
        comp_eval = None
        if feedback_in.comprehensive_evaluation:
            comp_eval = feedback_in.comprehensive_evaluation.dict()
        
        # 准备推荐意见
        hiring_rec = None
        if feedback_in.hiring_recommendation:
            # 检查是否是字符串类型
            if isinstance(feedback_in.hiring_recommendation, str):
                hiring_rec = feedback_in.hiring_recommendation
            else:
                # 如果是枚举类型，获取其value
                hiring_rec = feedback_in.hiring_recommendation.value
            
        # 执行更新
        query.update({
            "feedback": feedback_in.feedback,
            "evaluation_score": feedback_in.evaluation_score,
            "technical_evaluation": tech_eval,
            "comprehensive_evaluation": comp_eval,
            "strengths": feedback_in.strengths,
            "weaknesses": feedback_in.weaknesses,
            "hiring_recommendation": hiring_rec,
            "preparation_notes": feedback_in.preparation_notes,
            "process_record": feedback_in.process_record,
            "status": "completed"
        })
        
        db.commit()
        
        # 返回更新后的数据
        return self.get_interviewer_feedback(
            db=db,
            interview_id=feedback_in.interview_id,
            interviewer_id=feedback_in.interviewer_id
        )
    
    def get_interviewer_feedback(
        self,
        db: Session,
        interview_id: int,
        interviewer_id: int
    ) -> Optional[Dict[str, Any]]:
        """获取指定面试官的反馈"""
        # 查询面试官反馈
        feedback_row = db.query(
            models.interview_interviewers
        ).filter(
            models.interview_interviewers.c.interview_id == interview_id,
            models.interview_interviewers.c.interviewer_id == interviewer_id
        ).first()
        
        if not feedback_row:
            return None
        
        # 查询面试官信息
        interviewer = db.query(models.User).filter(
            models.User.id == interviewer_id
        ).first()
        
        if not interviewer:
            return None
        
        # 构建响应
        result = {
            "interview_id": interview_id,
            "interviewer_id": interviewer_id,
            "interviewer": {
                "id": interviewer.id,
                "full_name": interviewer.username,
                "email": interviewer.email
            },
            "feedback": feedback_row.feedback,
            "evaluation_score": feedback_row.evaluation_score,
            "technical_evaluation": feedback_row.technical_evaluation,
            "comprehensive_evaluation": feedback_row.comprehensive_evaluation,
            "strengths": feedback_row.strengths,
            "weaknesses": feedback_row.weaknesses,
            "hiring_recommendation": feedback_row.hiring_recommendation,
            "preparation_notes": feedback_row.preparation_notes,
            "process_record": feedback_row.process_record,
            "status": feedback_row.status,
            "created_at": feedback_row.created_at,
            "updated_at": feedback_row.updated_at
        }
        
        return result
    
    def update_feedback(
        self,
        db: Session,
        interview_id: int,
        interviewer_id: int,
        feedback_in: InterviewerFeedbackUpdate
    ) -> Dict[str, Any]:
        """更新面试官反馈"""
        # 准备更新数据
        update_data = {}
        
        if feedback_in.feedback is not None:
            update_data["feedback"] = feedback_in.feedback
        
        if feedback_in.evaluation_score is not None:
            update_data["evaluation_score"] = feedback_in.evaluation_score
        
        if feedback_in.technical_evaluation is not None:
            tech_eval = feedback_in.technical_evaluation.dict()
            update_data["technical_evaluation"] = tech_eval
        
        if feedback_in.comprehensive_evaluation is not None:
            comp_eval = feedback_in.comprehensive_evaluation.dict()
            update_data["comprehensive_evaluation"] = comp_eval
        
        if feedback_in.strengths is not None:
            update_data["strengths"] = feedback_in.strengths
        
        if feedback_in.weaknesses is not None:
            update_data["weaknesses"] = feedback_in.weaknesses
        
        if feedback_in.hiring_recommendation is not None:
            # 检查是否是字符串类型
            if isinstance(feedback_in.hiring_recommendation, str):
                rec = feedback_in.hiring_recommendation
                update_data["hiring_recommendation"] = rec
            else:
                # 如果是枚举类型，获取其value
                rec = feedback_in.hiring_recommendation.value
                update_data["hiring_recommendation"] = rec
        
        if feedback_in.preparation_notes is not None:
            update_data["preparation_notes"] = feedback_in.preparation_notes
        
        if feedback_in.process_record is not None:
            update_data["process_record"] = feedback_in.process_record
        
        # 当任何反馈字段被更新时，将状态设置为已完成
        if update_data:
            update_data["status"] = "completed"
        
        # 执行更新
        db.query(models.interview_interviewers).filter(
            models.interview_interviewers.c.interview_id == interview_id,
            models.interview_interviewers.c.interviewer_id == interviewer_id
        ).update(update_data)
        
        db.commit()
        
        # 返回更新后的数据
        return self.get_interviewer_feedback(
            db=db,
            interview_id=interview_id,
            interviewer_id=interviewer_id
        )
    
    def get_all_feedback(
        self,
        db: Session,
        interview_id: int
    ) -> List[Dict[str, Any]]:
        """获取面试的所有反馈"""
        # 查询所有面试官反馈
        feedback_rows = db.query(
            models.interview_interviewers
        ).filter(
            models.interview_interviewers.c.interview_id == interview_id
        ).all()
        
        # 获取所有相关的面试官ID
        interviewer_ids = [row.interviewer_id for row in feedback_rows]
        
        # 批量查询所有相关面试官
        interviewers = {
            user.id: user 
            for user in db.query(models.User).filter(
                models.User.id.in_(interviewer_ids)
            ).all()
        }
        
        # 构建响应
        result = []
        for row in feedback_rows:
            interviewer = interviewers.get(row.interviewer_id)
            if not interviewer:
                continue
                
            result.append({
                "interview_id": interview_id,
                "interviewer_id": interviewer.id,
                "interviewer_name": interviewer.username,
                "interviewer": {
                    "id": interviewer.id,
                    "full_name": interviewer.username,
                    "email": interviewer.email
                },
                "feedback": row.feedback,
                "evaluation_score": row.evaluation_score,
                "technical_evaluation": row.technical_evaluation,
                "comprehensive_evaluation": row.comprehensive_evaluation,
                "strengths": row.strengths,
                "weaknesses": row.weaknesses,
                "hiring_recommendation": row.hiring_recommendation,
                "preparation_notes": row.preparation_notes,
                "process_record": row.process_record,
                "status": row.status,
                "created_at": row.created_at,
                "updated_at": row.updated_at
            })
        
        return result
    
    def get_feedback_summary(
        self,
        db: Session,
        interview_id: int
    ) -> InterviewFeedbackSummary:
        """获取面试反馈汇总"""
        # 获取所有反馈
        all_feedbacks = self.get_all_feedback(db=db, interview_id=interview_id)
        
        # 如果没有反馈，返回空汇总
        if not all_feedbacks:
            return InterviewFeedbackSummary(
                interview_id=interview_id,
                average_score=0,
                interviewer_count=0,
                completed_count=0,
                feedbacks=[],
                recommendation_summary={},
                technical_averages={},
                comprehensive_averages={},
                key_strengths=[],
                key_weaknesses=[]
            )
        
        # 计算汇总数据
        scores = [
            f["evaluation_score"] 
            for f in all_feedbacks 
            if f["evaluation_score"] is not None
        ]
        average_score = statistics.mean(scores) if scores else 0
        
        completed_count = sum(
            1 for f in all_feedbacks if f["status"] == "completed"
        )
        
        # 收集推荐汇总
        recommendations = [
            f["hiring_recommendation"] 
            for f in all_feedbacks 
            if f["hiring_recommendation"] is not None
        ]
        recommendation_counter = Counter(recommendations)
        recommendation_summary = {
            key: value 
            for key, value in recommendation_counter.items()
        }
        
        # 计算技术评估和综合评估的平均分
        technical_fields = [
            "coding_ability", "problem_solving", "system_design",
            "algorithm", "knowledge_depth", "knowledge_breadth"
        ]
        comprehensive_fields = [
            "communication", "teamwork", "learning_ability",
            "pressure_handling", "cultural_fit"
        ]
        
        technical_scores = {field: [] for field in technical_fields}
        comprehensive_scores = {field: [] for field in comprehensive_fields}
        
        # 收集所有分数
        for feedback in all_feedbacks:
            if feedback["technical_evaluation"]:
                for field in technical_fields:
                    if feedback["technical_evaluation"].get(field) is not None:
                        tech_eval = feedback["technical_evaluation"]
                        technical_scores[field].append(tech_eval[field])
            
            if feedback["comprehensive_evaluation"]:
                for field in comprehensive_fields:
                    comp_eval = feedback["comprehensive_evaluation"]
                    if comp_eval.get(field) is not None:
                        comprehensive_scores[field].append(comp_eval[field])
        
        # 计算平均分
        technical_averages = {
            field: statistics.mean(scores) if scores else 0
            for field, scores in technical_scores.items()
        }
        
        comprehensive_averages = {
            field: statistics.mean(scores) if scores else 0
            for field, scores in comprehensive_scores.items()
        }
        
        # 收集优势和劣势
        all_strengths = []
        all_weaknesses = []
        
        for feedback in all_feedbacks:
            if feedback["strengths"]:
                all_strengths.extend([
                    s.strip() 
                    for s in feedback["strengths"].split(',')
                ])
            if feedback["weaknesses"]:
                all_weaknesses.extend([
                    w.strip() 
                    for w in feedback["weaknesses"].split(',')
                ])
        
        # 计算最常见的优势和劣势
        strength_counter = Counter(all_strengths)
        weakness_counter = Counter(all_weaknesses)
        
        key_strengths = [
            item 
            for item, count in strength_counter.most_common(5) 
            if item
        ]
        key_weaknesses = [
            item 
            for item, count in weakness_counter.most_common(5) 
            if item
        ]
        
        # 创建汇总对象
        summary = InterviewFeedbackSummary(
            interview_id=interview_id,
            average_score=average_score,
            interviewer_count=len(all_feedbacks),
            completed_count=completed_count,
            feedbacks=all_feedbacks,
            recommendation_summary=recommendation_summary,
            technical_averages=technical_averages,
            comprehensive_averages=comprehensive_averages,
            key_strengths=key_strengths,
            key_weaknesses=key_weaknesses
        )
        
        return summary
    
    def verify_interview_access(
        self,
        db: Session,
        interview_id: int,
        current_user: models.User
    ) -> bool:
        """
        验证面试存在性和用户访问权限
        
        Args:
            db: 数据库会话
            interview_id: 面试ID
            current_user: 当前用户
            
        Returns:
            True 如果通过验证
            
        Raises:
            HTTPException: 当面试不存在或用户无权限时
        """
        # 检查面试是否存在
        interview = db.query(models.Interview).filter(
            models.Interview.id == interview_id
        ).first()
        if not interview:
            raise HTTPException(status_code=404, detail="面试不存在")
        
        # 检查权限
        if not current_user.is_superuser:
            # 检查当前用户是否是面试的面试官之一
            query = models.interview_interviewers
            is_interviewer = db.query(query).filter(
                query.c.interview_id == interview_id,
                query.c.interviewer_id == current_user.id
            ).first()
            
            if not is_interviewer:
                raise HTTPException(
                    status_code=403,
                    detail="需要管理员权限或是该面试的面试官"
                )
        
        return True


# 创建服务实例
interview_feedback_service = InterviewFeedbackService() 