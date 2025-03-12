from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime, timedelta
from sqlalchemy import and_, or_

from app import models, schemas
from app.schemas.interview import InterviewCreate, InterviewUpdate
from .base import BaseService
from app.services import candidate_service


class InterviewService(BaseService[models.Interview, InterviewCreate, InterviewUpdate]):
    """面试服务"""
    
    def __init__(self):
        super().__init__(models.Interview)

    def search_interviews(
        self,
        db: Session,
        *,
        keyword: str = None,
        tenant_id: Optional[int] = None,
        candidate_id: Optional[int] = None,
        job_id: Optional[int] = None,
        status: Optional[str] = None,
        interviewer_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[models.Interview]:
        """搜索面试记录"""
        query = db.query(models.Interview)
        
        # 基础过滤条件
        filters = []
        if tenant_id is not None:
            filters.append(models.Interview.tenant_id == tenant_id)
        if candidate_id is not None:
            filters.append(models.Interview.candidate_id == candidate_id)
        if job_id is not None:
            filters.append(models.Interview.job_id == job_id)
        if status:
            filters.append(models.Interview.status == status)
        if interviewer_id:
            filters.append(models.Interview.interviewer_id == interviewer_id)
        if start_date:
            filters.append(models.Interview.interview_time >= start_date)
        if end_date:
            filters.append(models.Interview.interview_time <= end_date)
            
        # 关键词搜索
        if keyword:
            keyword_filter = or_(
                models.Interview.title.ilike(f"%{keyword}%"),
                models.Interview.location.ilike(f"%{keyword}%"),
                models.Interview.notes.ilike(f"%{keyword}%")
            )
            filters.append(keyword_filter)
            
        if filters:
            query = query.filter(and_(*filters))
            
        return query.offset(skip).limit(limit).all()

    async def schedule_interview(
        self,
        db: Session,
        *,
        candidate_id: int,
        job_id: int,
        interviewer_id: int,
        interview_time: datetime,
        duration: int = 60,
        title: Optional[str] = None,
        location: Optional[str] = None,
        interview_type: str = "onsite",
        notes: Optional[str] = None
    ) -> models.Interview:
        """安排面试"""
        # 检查候选人
        candidate = candidate_service.get(db, id=candidate_id)
        if not candidate:
            raise HTTPException(status_code=404, detail="候选人不存在")
            
        # 检查时间冲突
        end_time = interview_time + timedelta(minutes=duration)
        conflicts = db.query(models.Interview).filter(
            models.Interview.interviewer_id == interviewer_id,
            models.Interview.status.in_(["scheduled", "in_progress"]),
            or_(
                and_(
                    models.Interview.interview_time <= interview_time,
                    models.Interview.interview_end_time > interview_time
                ),
                and_(
                    models.Interview.interview_time < end_time,
                    models.Interview.interview_end_time >= end_time
                )
            )
        ).all()
        
        if conflicts:
            raise HTTPException(
                status_code=400,
                detail="面试官在该时间段已有其他面试安排"
            )
            
        # 创建面试记录
        interview_in = InterviewCreate(
            candidate_id=candidate_id,
            job_id=job_id,
            interviewer_id=interviewer_id,
            tenant_id=candidate.tenant_id,
            title=title or f"{candidate.name}的面试",
            location=location,
            interview_type=interview_type,
            interview_time=interview_time,
            interview_end_time=end_time,
            duration=duration,
            notes=notes,
            status="scheduled"
        )
        
        interview = self.create(db=db, obj_in=interview_in)
        
        # 更新候选人状态
        await candidate_service.update_candidate_status(
            db,
            candidate_id=candidate_id,
            status="interviewing",
            note=f"已安排面试: {title}"
        )
        
        return interview

    async def update_interview_status(
        self,
        db: Session,
        *,
        interview_id: int,
        status: str,
        feedback: Optional[Dict[str, Any]] = None,
        evaluation_score: Optional[float] = None,
        notes: Optional[str] = None
    ) -> models.Interview:
        """更新面试状态"""
        interview = self.get(db, id=interview_id)
        if not interview:
            raise HTTPException(status_code=404, detail="面试不存在")
            
        update_data = {
            "status": status,
            "status_updated_at": datetime.utcnow()
        }
        
        if status == "completed":
            if not feedback:
                raise HTTPException(
                    status_code=400,
                    detail="面试完成需要提供反馈"
                )
            update_data.update({
                "feedback": feedback,
                "evaluation_score": evaluation_score,
                "completed_at": datetime.utcnow()
            })
            
            # 更新候选人状态
            await candidate_service.update_candidate_status(
                db,
                candidate_id=interview.candidate_id,
                status="interviewed",
                note=f"面试完成,评分:{evaluation_score}"
            )
            
        elif status == "cancelled":
            if not notes:
                raise HTTPException(
                    status_code=400,
                    detail="取消面试需要提供原因"
                )
            update_data["notes"] = notes
            
            # 更新候选人状态
            await candidate_service.update_candidate_status(
                db,
                candidate_id=interview.candidate_id,
                status="pending",
                note=f"面试取消,原因:{notes}"
            )
            
        interview = self.update(
            db,
            db_obj=interview,
            obj_in=InterviewUpdate(**update_data)
        )
        
        return interview

    def get_interviewer_schedule(
        self,
        db: Session,
        *,
        interviewer_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """获取面试官的面试安排"""
        interviews = db.query(models.Interview).filter(
            models.Interview.interviewer_id == interviewer_id,
            models.Interview.interview_time >= start_date,
            models.Interview.interview_time <= end_date,
            models.Interview.status.in_(["scheduled", "in_progress"])
        ).order_by(
            models.Interview.interview_time
        ).all()
        
        return [
            {
                "interview_id": i.id,
                "title": i.title,
                "candidate_name": i.candidate.name,
                "job_title": i.job.title,
                "interview_time": i.interview_time,
                "duration": i.duration,
                "location": i.location,
                "type": i.interview_type,
                "status": i.status
            }
            for i in interviews
        ]


# 创建服务实例
interview_service = InterviewService()

# 只导出实例
__all__ = ["interview_service"] 