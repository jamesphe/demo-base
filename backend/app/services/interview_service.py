from sqlalchemy import and_, or_
from typing import Any, List, Dict, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from fastapi import HTTPException
import sqlalchemy.orm

from app import models, crud, schemas
from app.schemas.interview import InterviewCreate, InterviewUpdate, InterviewType
from .base import BaseService
from app.services import resume_service
from app.services.job_application_service import job_application_service


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
        resume_id: Optional[int] = None,
        job_id: Optional[int] = None,
        status: Optional[str] = None,
        interviewer_id: Optional[int] = None,
        interview_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[models.Interview]:
        """搜索面试记录"""
        # 使用options预加载相关数据
        query = db.query(models.Interview).options(
            sqlalchemy.orm.joinedload(models.Interview.resume),
            sqlalchemy.orm.joinedload(models.Interview.job),
            sqlalchemy.orm.joinedload(models.Interview.interviewers)
        )
        
        # 基础过滤条件
        filters = []
        if tenant_id is not None:
            filters.append(models.Interview.tenant_id == tenant_id)
        if resume_id is not None:
            filters.append(models.Interview.resume_id == resume_id)
        if job_id is not None:
            filters.append(models.Interview.job_id == job_id)
        if status:
            filters.append(models.Interview.status == status)
        if interview_type:
            filters.append(models.Interview.interview_type == interview_type)
        if interviewer_id:
            # 修改为通过关联表查询
            query = query.join(models.interview_interviewers)
            filters.append(models.interview_interviewers.c.interviewer_id == interviewer_id)
        if start_date:
            filters.append(models.Interview.schedule_time >= start_date)
        if end_date:
            filters.append(models.Interview.schedule_time <= end_date)
            
        # 关键词搜索
        if keyword:
            keyword_filter = or_(
                models.Interview.feedback.ilike(f"%{keyword}%")
            )
            filters.append(keyword_filter)
            
        if filters:
            query = query.filter(and_(*filters))
        
        # 添加distinct避免因为join造成的重复
        if interviewer_id:
            query = query.distinct()
            
        interviews = query.offset(skip).limit(limit).all()
        
        # 为每个面试记录添加额外信息
        for interview in interviews:
            if interview.resume:
                interview.resume_title = interview.resume.name
            if interview.job:
                interview.job_title = interview.job.title
            # 获取所有面试官的名字
            interview.interviewer_names = [interviewer.username for interviewer in interview.interviewers] if interview.interviewers else []
            
        return interviews

    def schedule_interview(
        self,
        db: Session,
        *,
        resume_id: int,
        job_id: int,
        interviewer_ids: List[int],  # 修改为面试官ID列表
        interview_time: datetime,
        duration: int = 60,
        location: Optional[str] = None,
        interview_type: InterviewType = InterviewType.FIRST,
        notes: Optional[str] = None,
        current_user: Optional[models.User] = None
    ) -> models.Interview:
        """安排面试"""
        import logging
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        
        try:
            # 验证简历存在
            resume = db.query(models.Resume).filter(models.Resume.id == resume_id).first()
            if not resume:
                logger.error(f"简历 {resume_id} 不存在")
                raise ValueError(f"简历 {resume_id} 不存在")
                
            # 验证职位存在
            job = db.query(models.Job).filter(models.Job.id == job_id).first()
            if not job:
                logger.error(f"职位 {job_id} 不存在")
                raise ValueError(f"职位 {job_id} 不存在")
                
            # 验证所有面试官存在
            for interviewer_id in interviewer_ids:
                interviewer = db.query(models.User).filter(models.User.id == interviewer_id).first()
                if not interviewer:
                    logger.error(f"面试官 {interviewer_id} 不存在")
                    raise ValueError(f"面试官 {interviewer_id} 不存在")
                
            # 检查时间冲突
            end_time = interview_time + timedelta(minutes=duration)
            
            # 检查每个面试官的时间冲突
            for interviewer_id in interviewer_ids:
                conflicts = (
                    db.query(models.Interview)
                    .join(models.interview_interviewers)
                    .filter(
                        models.interview_interviewers.c.interviewer_id == interviewer_id,
                        models.Interview.status.in_(["scheduled", "in_progress"]),
                        or_(
                            and_(
                                models.Interview.schedule_time <= interview_time,
                                models.Interview.schedule_time + timedelta(minutes=60) > interview_time
                            ),
                            and_(
                                models.Interview.schedule_time < end_time,
                                models.Interview.schedule_time + timedelta(minutes=60) >= end_time
                            )
                        )
                    )
                    .all()
                )
                
                if conflicts:
                    logger.error(f"面试官 {interviewer_id} 在该时间段已有其他面试安排")
                    raise ValueError(f"面试官 {interviewer_id} 在该时间段已有其他面试安排")
                
            # 处理interview_type
            interview_type_value = None
            if isinstance(interview_type, InterviewType):
                interview_type_value = interview_type.value
            elif isinstance(interview_type, str):
                if interview_type in [e.value for e in InterviewType]:
                    interview_type_value = interview_type
                else:
                    logger.warning(f"未知的面试类型 {interview_type}，使用默认值")
                    interview_type_value = InterviewType.FIRST.value
            else:
                logger.warning(f"无效的面试类型 {interview_type}，使用默认值")
                interview_type_value = InterviewType.FIRST.value
                
            # 创建面试记录
            interview_obj = models.Interview(
                resume_id=resume_id,
                job_id=job_id,
                tenant_id=resume.tenant_id,
                location=location or "",
                interview_type=interview_type_value,
                schedule_time=interview_time,
                duration=duration,
                notes=notes,
                status="scheduled"
            )
            
            db.add(interview_obj)
            db.flush()  # 获取ID但不提交
            
            # 添加面试官关联
            for interviewer_id in interviewer_ids:
                db.execute(
                    models.interview_interviewers.insert().values(
                        interview_id=interview_obj.id,
                        interviewer_id=interviewer_id
                    )
                )
            
            db.commit()
            db.refresh(interview_obj)
            
            # 更新简历状态
            resume_service.update_resume_status(
                db,
                resume_id=resume_id,
                status="interviewing",
                note=f"已安排{interview_type_value}面试"
            )
            
            # 更新职位申请状态
            job_application = db.query(models.JobApplication).filter(
                models.JobApplication.job_id == job_id,
                models.JobApplication.resume_id == resume_id
            ).first()
            
            if job_application:
                job_application_service.update_application_status(
                    db,
                    application_id=job_application.id,
                    status="interview_scheduled",
                    review_notes=f"已安排{interview_type_value}面试",
                    current_user=current_user
                )
            
            return interview_obj
        except Exception as e:
            logger.error(f"安排面试失败: {str(e)}")
            raise ValueError(f"安排面试失败: {str(e)}")

    def update_interview_status(
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
        
        # 直接更新面试状态，而不是创建完整的InterviewUpdate对象
        update_data = {
            "status": status,
            "status_updated_at": datetime.utcnow()
        }
        
        if status == "completed":
            # 只更新完成时间，不更新反馈和评分
            update_data.update({
                "completed_at": datetime.utcnow()
            })
            
            # 更新简历状态
            resume_service.update_resume_status(
                db,
                resume_id=interview.resume_id,
                status="interviewed",
                note="面试已完成"
            )
            
        elif status == "cancelled":
            if not notes:
                raise HTTPException(
                    status_code=400,
                    detail="取消面试需要提供原因"
                )
            update_data["notes"] = notes
            
            # 更新简历状态
            resume_service.update_resume_status(
                db,
                resume_id=interview.resume_id,
                status="pending",
                note=f"面试取消,原因:{notes}"
            )
        
        # 直接使用SQLAlchemy更新面试记录
        for key, value in update_data.items():
            setattr(interview, key, value)
        db.commit()
        db.refresh(interview)
        
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
        interviews = (
            db.query(models.Interview)
            .join(models.interview_interviewers)
            .filter(
                models.interview_interviewers.c.interviewer_id == interviewer_id,
                models.Interview.schedule_time >= start_date,
                models.Interview.schedule_time <= end_date,
                models.Interview.status.in_(["scheduled", "in_progress"])
            )
            .order_by(models.Interview.schedule_time)
            .all()
        )
        
        return [
            {
                "interview_id": i.id,
                "resume_title": i.resume.name,
                "job_title": i.job.title,
                "schedule_time": i.schedule_time,
                "duration": i.duration,
                "location": i.location,
                "type": i.interview_type,
                "status": i.status
            }
            for i in interviews
        ]
        
    def get_interviewers(self, db: Session, tenant_id: int = None, page: int = 1, per_page: int = 10):
        """获取面试官列表"""
        skip = (page - 1) * per_page
        # 获取有interviewer角色的用户
        query = db.query(models.User).join(
            models.UserRole,
            models.User.id == models.UserRole.user_id
        ).join(
            models.Role,
            models.Role.id == models.UserRole.role_id
        ).filter(
            models.Role.name == "interviewer"
        ).options(
            # 预加载租户信息
            sqlalchemy.orm.joinedload(models.User.tenant),
            sqlalchemy.orm.joinedload(models.User.roles)
        )
        
        # 如果指定了租户，则只获取该租户的面试官
        if tenant_id:
            query = query.filter(models.User.tenant_id == tenant_id)
        
        total = query.count()
        interviewers = query.offset(skip).limit(per_page).all()
        
        # 手动处理结果，确保包含必要的租户信息
        processed_interviewers = []
        for interviewer in interviewers:
            interviewer_dict = {
                "id": interviewer.id,
                "username": interviewer.username,
                "email": interviewer.email,
                "user_type": interviewer.user_type,
                "avatar": interviewer.avatar,
                "introduction": interviewer.introduction,
                "is_active": interviewer.is_active,
                "is_superuser": interviewer.is_superuser,
                "tenant_id": interviewer.tenant_id,
                "phone": interviewer.phone,
                "created_at": interviewer.created_at,
                "updated_at": interviewer.updated_at,
                "role_names": [role.name for role in interviewer.roles] if interviewer.roles else [],
                "roles": [{"id": role.id, "name": role.name, "description": role.description} 
                         for role in interviewer.roles] if interviewer.roles else []
            }
            
            # 确保租户信息完整
            if interviewer.tenant:
                interviewer_dict["tenant"] = {
                    "id": interviewer.tenant.id,
                    "name": interviewer.tenant.tenant_name,
                    "code": interviewer.tenant.external_id or ""
                }
                interviewer_dict["tenant_name"] = interviewer.tenant.tenant_name
            else:
                interviewer_dict["tenant"] = None
                interviewer_dict["tenant_name"] = None
                
            processed_interviewers.append(interviewer_dict)
            
        return {
            "data": processed_interviewers,
            "meta": {
                "total": total,
                "page": page,
                "per_page": per_page,
                "total_pages": (total + per_page - 1) // per_page
            }
        }
        
    def update_interview_preparation(
        self,
        db: Session,
        interview_id: int,
        current_user: models.User,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """更新面试准备信息
        
        Args:
            db: 数据库会话
            interview_id: 面试ID
            current_user: 当前用户
            data: 包含focusPoints、role和interviewGuide的字典
            
        Returns:
            包含状态信息的字典
            
        Raises:
            HTTPException: 当面试不存在或用户无权限时
        """
        # 检查面试是否存在
        interview = self.get(db, id=interview_id)
        if not interview:
            raise HTTPException(status_code=404, detail="面试不存在")
        
        # 检查当前用户是否是面试官
        is_interviewer = db.query(models.interview_interviewers).filter(
            models.interview_interviewers.c.interview_id == interview_id,
            models.interview_interviewers.c.interviewer_id == current_user.id
        ).first()
        
        if not is_interviewer and not current_user.is_superuser:
            raise HTTPException(
                status_code=403,
                detail="您不是该面试的面试官，无法更新准备信息"
            )
        
        # 解析请求数据
        role = data.get("role", "")
        interview_guide = data.get("interviewGuide", "")
        
        # 合并数据为Markdown格式的准备笔记
        preparation_notes = f"""# {role}面试准备

{interview_guide}
"""
        
        # 更新面试官关联表中的准备笔记
        from sqlalchemy import update
        db.execute(
            update(models.interview_interviewers).where(
                models.interview_interviewers.c.interview_id == interview_id,
                models.interview_interviewers.c.interviewer_id == current_user.id
            ).values(
                preparation_notes=preparation_notes,
                updated_at=datetime.utcnow()
            )
        )
        db.commit()
        
        return {
            "status": "success",
            "message": "面试准备信息已更新"
        }
        
    def get_interview_preparation(
        self,
        db: Session,
        interview_id: int,
        current_user: models.User
    ) -> Dict[str, Any]:
        """获取面试准备信息
        
        Args:
            db: 数据库会话
            interview_id: 面试ID
            current_user: 当前用户
            
        Returns:
            包含面试准备信息的字典
            
        Raises:
            HTTPException: 当面试不存在或用户无权限时
        """
        # 检查面试是否存在
        interview = self.get(db, id=interview_id)
        if not interview:
            raise HTTPException(status_code=404, detail="面试不存在")
        
        # 检查权限
        if not current_user.is_superuser:
            # 检查当前用户是否是面试的面试官之一
            is_interviewer = db.query(models.interview_interviewers).filter(
                models.interview_interviewers.c.interview_id == interview_id,
                models.interview_interviewers.c.interviewer_id == current_user.id
            ).first()
            
            if not is_interviewer:
                raise HTTPException(
                    status_code=403,
                    detail="需要管理员权限或是该面试的面试官"
                )
        
        # 获取面试准备信息
        preparation_info = {
            "interview_id": interview_id,
            "preparation_notes": "",  # 从面试官关联表中获取
            "focus_points": []  # 从预定义的关注点中获取
        }
        
        # 处理Resume对象
        if interview.resume:
            preparation_info["resume"] = {
                "id": interview.resume.id,
                "name": interview.resume.name,
                "phone": interview.resume.phone,
                "email": interview.resume.email,
                "gender": interview.resume.gender,
                "highest_education": interview.resume.highest_education,
                "major": interview.resume.major,
                "experience_years": interview.resume.experience_years,
                "current_company": interview.resume.current_company,
                "current_position": interview.resume.current_position
            }
        else:
            preparation_info["resume"] = None
            
        # 处理Job对象
        if interview.job:
            preparation_info["job"] = {
                "id": interview.job.id,
                "title": interview.job.title,
                "department": getattr(interview.job, "department", None),
                "job_type": interview.job.job_type,
                "description": interview.job.description,
                "requirements": interview.job.requirements
            }
        else:
            preparation_info["job"] = None
        
        # 获取当前面试官的准备笔记
        if not current_user.is_superuser:
            interviewer_notes = db.query(models.interview_interviewers).filter(
                models.interview_interviewers.c.interview_id == interview_id,
                models.interview_interviewers.c.interviewer_id == current_user.id
            ).first()
            
            if interviewer_notes:
                preparation_info["preparation_notes"] = interviewer_notes.preparation_notes or ""
        
        return preparation_info
        
    def get_interviewer_focus_points(self) -> Dict[str, List[Dict]]:
        """获取面试官关注点列表
        
        Returns:
            包含关注点列表的字典
        """
        # 返回预定义的关注点列表
        focus_points = [
            {
                "id": 1,
                "category": "技术能力",
                "points": [
                    "编程语言掌握程度",
                    "算法和数据结构",
                    "系统设计能力",
                    "代码质量和风格",
                    "问题解决能力"
                ]
            },
            {
                "id": 2,
                "category": "项目经验",
                "points": [
                    "项目规模和复杂度",
                    "技术选型判断",
                    "架构设计经验",
                    "性能优化经验",
                    "项目管理能力"
                ]
            },
            {
                "id": 3,
                "category": "软技能",
                "points": [
                    "沟通表达能力",
                    "团队协作能力",
                    "学习能力",
                    "抗压能力",
                    "职业规划"
                ]
            }
        ]
        
        return {"data": focus_points}


# 创建服务实例
interview_service = InterviewService()

# 只导出实例
__all__ = ["interview_service"] 