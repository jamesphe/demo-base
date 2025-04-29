from app.services.resume_service import resume_service
from app.db.session import SessionLocal
from typing import List, Optional
import logging
from app import models
from app.core.celery_config import celery_app

logger = logging.getLogger(__name__)


class ResumeQueueService:
    def __init__(self):
        self.db = SessionLocal()
    
    def get_pending_resumes(self, limit: int = 10) -> List[models.Resume]:
        """获取待处理的简历"""
        return self.db.query(models.Resume).filter(
            models.Resume.processing_status == 'pending'
        ).limit(limit).all()


@celery_app.task(
    name='app.services.resume_queue_service.process_pending_resumes'
)
def process_pending_resumes():
    """处理待处理的简历"""
    service = ResumeQueueService()
    try:
        pending_resumes = service.get_pending_resumes()
        for resume in pending_resumes:
            # 获取简历最新的职位申请记录
            latest_application = (
                service.db.query(models.JobApplication)
                .filter(models.JobApplication.resume_id == resume.id)
                .order_by(models.JobApplication.created_at.desc())
                .first()
            )
            
            job_id = latest_application.job_id if latest_application else None
            
            process_resume_task.delay(
                resume.id,
                **{
                    'publisher_id': resume.publisher_id,
                    'job_id': job_id
                }
            )
    except Exception as e:
        logger.error(f"处理待处理简历失败: {str(e)}")


@celery_app.task(name='app.services.resume_queue_service.process_resume_task')
def process_resume_task(resume_id: int, **kwargs):
    """处理单个简历的 Celery 任务"""
    db = SessionLocal()
    try:
        resume = db.query(models.Resume).filter(
            models.Resume.id == resume_id
        ).first()
        
        if not resume:
            logger.error(f"简历不存在: {resume_id}")
            return
        
        # 更新状态为处理中
        resume.processing_status = 'processing'
        db.commit()
        
        # 处理简历
        resume_service.process_resume_sync(
            resume_id=resume.id,
            publisher_id=kwargs.get('publisher_id'),
            job_id=kwargs.get('job_id'),
            job_external_id=kwargs.get('job_external_id')
        )
        
    except Exception as e:
        logger.error(f"处理简历失败: {resume_id}: {str(e)}")
        if resume:
            resume.processing_status = 'failed'
            resume.processing_error = str(e)
            db.commit()
    finally:
        db.close()


# 创建服务实例
resume_queue_service = ResumeQueueService() 