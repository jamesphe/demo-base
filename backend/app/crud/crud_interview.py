from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from app.crud.base import CRUDBase
from app.models.interview import Interview, interview_interviewers
from app.schemas.interview import InterviewCreate, InterviewUpdate


class CRUDInterview(CRUDBase[Interview, InterviewCreate, InterviewUpdate]):
    def get_multi_by_tenant(
        self,
        db: Session,
        *,
        tenant_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Interview]:
        """获取指定租户的面试列表"""
        return (
            db.query(Interview)
            .join(Interview.resume)
            .filter(Interview.resume.has(tenant_id=tenant_id))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_multi_with_details(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[Interview]:
        """获取面试列表，包含完整的简历和面试官信息"""
        interviews = (
            db.query(Interview)
            .options(
                joinedload(Interview.resume),
                joinedload(Interview.job),
                joinedload(Interview.interviewers)
            )
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        # 添加额外信息到每个面试记录
        for interview in interviews:
            if interview.resume:
                interview.resume_title = interview.resume.name
            if interview.job:
                interview.job_title = interview.job.title
            # 获取所有面试官的名字
            interview.interviewer_names = [interviewer.username for interviewer in interview.interviewers] if interview.interviewers else []
                
        return interviews

    def get_multi_by_tenant_with_details(
        self,
        db: Session,
        *,
        tenant_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Interview]:
        """获取指定租户的面试列表，包含完整的简历和面试官信息"""
        interviews = (
            db.query(Interview)
            .options(
                joinedload(Interview.resume),
                joinedload(Interview.job),
                joinedload(Interview.interviewers)
            )
            .join(Interview.resume)
            .filter(Interview.resume.has(tenant_id=tenant_id))
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        # 添加额外信息到每个面试记录
        for interview in interviews:
            if interview.resume:
                interview.resume_title = interview.resume.name
            if interview.job:
                interview.job_title = interview.job.title
            # 获取所有面试官的名字
            interview.interviewer_names = [interviewer.username for interviewer in interview.interviewers] if interview.interviewers else []
                
        return interviews

    def count_by_tenant(self, db: Session, *, tenant_id: int) -> int:
        """获取指定租户的面试总数"""
        return (
            db.query(Interview)
            .join(Interview.resume)
            .filter(Interview.resume.has(tenant_id=tenant_id))
            .count()
        )

    def get_by_resume(
        self,
        db: Session,
        *,
        resume_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Interview]:
        """获取指定简历的面试记录"""
        return (
            db.query(Interview)
            .filter(Interview.resume_id == resume_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_job(
        self,
        db: Session,
        *,
        job_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Interview]:
        """获取指定职位的面试记录"""
        return (
            db.query(Interview)
            .filter(Interview.job_id == job_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_interviewer(
        self,
        db: Session,
        *,
        interviewer_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Interview]:
        """获取指定面试官的面试记录"""
        return (
            db.query(Interview)
            .join(Interview.interviewers)
            .filter(interview_interviewers.c.interviewer_id == interviewer_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_scheduled_interviews(
        self,
        db: Session,
        *,
        start_time: datetime,
        end_time: datetime
    ) -> List[Interview]:
        """获取指定时间范围内的已安排面试"""
        return (
            db.query(Interview)
            .filter(
                Interview.schedule_time >= start_time,
                Interview.schedule_time <= end_time,
                Interview.status == "scheduled"
            )
            .all()
        )
    
    def create_with_interviewers(
        self,
        db: Session,
        *,
        obj_in: InterviewCreate,
        interviewer_ids: List[int]
    ) -> Interview:
        """创建面试并关联面试官"""
        # 过滤掉InterviewCreate中的非Interview模型字段
        interview_data = {
            key: value for key, value in obj_in.dict().items()
            if key not in ["interviewers", "type", "time", "candidates"]
        }
        
        # 创建面试对象
        db_obj = Interview(**interview_data)
        db.add(db_obj)
        db.flush()  # 获取ID但不提交
        
        # 添加面试官关联
        if interviewer_ids:
            for interviewer_id in interviewer_ids:
                # 直接插入多对多关系表
                db.execute(
                    interview_interviewers.insert().values(
                        interview_id=db_obj.id,
                        interviewer_id=interviewer_id
                    )
                )
        
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update_with_interviewers(
        self,
        db: Session,
        *,
        db_obj: Interview,
        obj_in: InterviewUpdate,
        interviewer_ids: Optional[List[int]] = None
    ) -> Interview:
        """更新面试并更新面试官关联"""
        # 首先更新基本信息
        update_data = obj_in.dict(exclude_unset=True)
        
        # 移除非Interview模型字段
        if "interviewers" in update_data:
            del update_data["interviewers"]
        
        # 更新面试对象基本信息
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        # 如果提供了面试官ID列表，则更新面试官关联
        if interviewer_ids is not None:
            # 删除所有现有关联
            db.execute(
                interview_interviewers.delete().where(
                    interview_interviewers.c.interview_id == db_obj.id
                )
            )
            
            # 添加新的关联
            for interviewer_id in interviewer_ids:
                db.execute(
                    interview_interviewers.insert().values(
                        interview_id=db_obj.id,
                        interviewer_id=interviewer_id
                    )
                )
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def count_by_interviewer(
        self,
        db: Session,
        *,
        interviewer_id: int
    ) -> int:
        """获取指定面试官的面试总数"""
        return (
            db.query(Interview)
            .join(Interview.interviewers)
            .filter(
                interview_interviewers.c.interviewer_id == interviewer_id
            )
            .count()
        )

    def get_by_candidate(
        self,
        db: Session,
        *,
        candidate_id: int
    ) -> List[Interview]:
        """获取候选人的面试记录"""
        # 通过简历表关联查询
        interviews = (
            db.query(Interview)
            .join(Interview.resume)
            .filter(
                Interview.resume.has(talent_id=candidate_id)
            )
            .all()
        )
        return interviews


interview = CRUDInterview(Interview) 