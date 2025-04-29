from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

# 创建Celery实例
celery_app = Celery(
    'resume_processor',
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        'app.services.resume_queue_service',
        'app.services.resume_sync_email_service'
    ]  # 添加任务模块
)

# 配置Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Shanghai',
    enable_utc=True,
    beat_schedule={
        'process-pending-resumes': {
            'task': 'app.services.resume_queue_service.process_pending_resumes',
            'schedule': crontab(minute='*/5'),  # 每5分钟执行一次
        },
        'sync-resume-emails': {
            'task': 'app.services.resume_sync_email_service.sync_all_emails',
            'schedule': crontab(minute='*/5'),  # 每15分钟执行一次
        },
    }
) 