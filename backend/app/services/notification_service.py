from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime
from sqlalchemy import and_, or_

from app import models, schemas
from app.schemas.notification import NotificationCreate, NotificationUpdate
from .base import BaseService


class NotificationService(BaseService[models.Notification, NotificationCreate, NotificationUpdate]):
    """通知服务"""
    
    def __init__(self):
        super().__init__(models.Notification)

    async def create_notification(
        self,
        db: Session,
        *,
        user_id: int,
        title: str,
        content: str,
        notification_type: str,
        related_id: Optional[int] = None,
        tenant_id: Optional[int] = None,
        priority: str = "normal"
    ) -> models.Notification:
        """创建通知"""
        notification_in = NotificationCreate(
            user_id=user_id,
            title=title,
            content=content,
            notification_type=notification_type,
            related_id=related_id,
            tenant_id=tenant_id,
            priority=priority,
            status="unread",
            created_at=datetime.utcnow()
        )
        
        return self.create(db=db, obj_in=notification_in)

    def get_user_notifications(
        self,
        db: Session,
        *,
        user_id: int,
        status: Optional[str] = None,
        notification_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[models.Notification]:
        """获取用户的通知"""
        query = db.query(models.Notification).filter(
            models.Notification.user_id == user_id
        )
        
        if status:
            query = query.filter(models.Notification.status == status)
        if notification_type:
            query = query.filter(models.Notification.notification_type == notification_type)
        if start_date:
            query = query.filter(models.Notification.created_at >= start_date)
        if end_date:
            query = query.filter(models.Notification.created_at <= end_date)
            
        return query.order_by(
            models.Notification.priority.desc(),
            models.Notification.created_at.desc()
        ).offset(skip).limit(limit).all()

    async def mark_as_read(
        self,
        db: Session,
        *,
        notification_id: int,
        user_id: int
    ) -> models.Notification:
        """标记通知为已读"""
        notification = self.get(db, id=notification_id)
        if not notification:
            raise HTTPException(status_code=404, detail="通知不存在")
            
        if notification.user_id != user_id:
            raise HTTPException(status_code=403, detail="无权操作此通知")
            
        return self.update(
            db,
            db_obj=notification,
            obj_in=NotificationUpdate(
                status="read",
                read_at=datetime.utcnow()
            )
        )

    async def mark_all_as_read(
        self,
        db: Session,
        *,
        user_id: int,
        notification_type: Optional[str] = None
    ) -> int:
        """标记所有通知为已读"""
        query = db.query(models.Notification).filter(
            models.Notification.user_id == user_id,
            models.Notification.status == "unread"
        )
        
        if notification_type:
            query = query.filter(models.Notification.notification_type == notification_type)
            
        count = query.update({
            "status": "read",
            "read_at": datetime.utcnow()
        })
        
        db.commit()
        return count

    async def send_interview_notification(
        self,
        db: Session,
        *,
        interview_id: int
    ) -> List[models.Notification]:
        """发送面试相关通知"""
        interview = db.query(models.Interview).get(interview_id)
        if not interview:
            raise HTTPException(status_code=404, detail="面试不存在")
            
        notifications = []
        
        # 通知候选人
        candidate_notification = await self.create_notification(
            db,
            user_id=interview.candidate.user_id,
            title="面试通知",
            content=f"您有一场面试安排在 {interview.interview_time}",
            notification_type="interview",
            related_id=interview_id,
            tenant_id=interview.tenant_id,
            priority="high"
        )
        notifications.append(candidate_notification)
        
        # 通知面试官
        interviewer_notification = await self.create_notification(
            db,
            user_id=interview.interviewer_id,
            title="面试安排",
            content=f"您有一场面试安排在 {interview.interview_time}",
            notification_type="interview",
            related_id=interview_id,
            tenant_id=interview.tenant_id,
            priority="high"
        )
        notifications.append(interviewer_notification)
        
        return notifications

    async def send_resume_notification(
        self,
        db: Session,
        *,
        resume_id: str,
        notification_type: str,
        user_ids: List[int]
    ) -> List[models.Notification]:
        """发送简历相关通知"""
        resume = db.query(models.Resume).filter(
            models.Resume.resume_id == resume_id
        ).first()
        if not resume:
            raise HTTPException(status_code=404, detail="简历不存在")
            
        notifications = []
        
        for user_id in user_ids:
            if notification_type == "new_resume":
                title = "新简历提醒"
                content = f"收到新简历: {resume.name}"
            elif notification_type == "resume_parsed":
                title = "简历解析完成"
                content = f"简历 {resume.name} 已完成解析"
            else:
                title = "简历通知"
                content = f"简历 {resume.name} 有新的更新"
                
            notification = await self.create_notification(
                db,
                user_id=user_id,
                title=title,
                content=content,
                notification_type=notification_type,
                related_id=resume.id,
                tenant_id=resume.tenant_id
            )
            notifications.append(notification)
            
        return notifications


# 创建服务实例
notification_service = NotificationService()

# 只导出实例
__all__ = ["notification_service"] 