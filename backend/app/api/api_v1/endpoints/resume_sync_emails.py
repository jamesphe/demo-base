from typing import Any, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app import models, schemas
from app.api import deps
from app.services.resume_sync_email_service import ResumeSyncEmailService

router = APIRouter()
service = ResumeSyncEmailService()


@router.post(
    "",
    response_model=schemas.ResumeSyncEmail,
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["resume_sync_email_create"]
            )
        )
    ]
)
def create_sync_email(
    *,
    db: Session = Depends(deps.get_db),
    sync_email_in: schemas.ResumeSyncEmailCreate,
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """创建简历同步邮箱配置"""
    # 调用服务层方法
    return service.create_sync_email(
        db, 
        sync_email_in, 
        current_user.tenant_id
    )


@router.get(
    "",
    response_model=schemas.ResumeSyncEmailListResponse,
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["resume_sync_email_read"]
            )
        )
    ]
)
def read_sync_emails(
    db: Session = Depends(deps.get_db),
    page: int = Query(1, ge=1, description="页码"),
    per_page: int = Query(10, ge=1, le=100, description="每页数量"),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """获取简历同步邮箱配置列表"""
    # 调用服务层方法
    return service.get_sync_emails(
        db,
        page,
        per_page,
        current_user.tenant_id,
        current_user.is_superuser
    )


@router.get(
    "/{sync_email_id}",
    response_model=schemas.ResumeSyncEmail,
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["resume_sync_email_read"]
            )
        )
    ]
)
def read_sync_email(
    *,
    db: Session = Depends(deps.get_db),
    sync_email_id: int,
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """获取单个简历同步邮箱配置"""
    # 调用服务层方法
    return service.get_sync_email(
        db,
        sync_email_id,
        current_user.tenant_id,
        current_user.is_superuser
    )


@router.put(
    "/{sync_email_id}",
    response_model=schemas.ResumeSyncEmail,
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["resume_sync_email_update"]
            )
        )
    ]
)
def update_sync_email(
    *,
    db: Session = Depends(deps.get_db),
    sync_email_id: int,
    sync_email_in: schemas.ResumeSyncEmailUpdate,
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """更新简历同步邮箱配置"""
    # 调用服务层方法
    return service.update_sync_email(
        db,
        sync_email_id,
        sync_email_in,
        current_user.tenant_id,
        current_user.is_superuser
    )


@router.delete(
    "/{sync_email_id}",
    response_model=schemas.ResponseMsg,
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["resume_sync_email_delete"]
            )
        )
    ]
)
def delete_sync_email(
    *,
    db: Session = Depends(deps.get_db),
    sync_email_id: int,
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """删除简历同步邮箱配置"""
    # 调用服务层方法
    return service.delete_sync_email(
        db,
        sync_email_id,
        current_user.tenant_id,
        current_user.is_superuser
    )


@router.post(
    "/{sync_email_id}/keywords",
    response_model=schemas.JobKeyword,
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["resume_sync_email_update"]
            )
        )
    ]
)
def create_keyword(
    *,
    db: Session = Depends(deps.get_db),
    sync_email_id: int,
    keyword_in: schemas.JobKeywordCreate,
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """创建职位关键字"""
    # 添加调试代码
    import logging
    logger = logging.getLogger(__name__)
    
    # 检查邮箱是否存在及同步状态
    sync_email = db.query(models.ResumeSyncEmail).filter(
        models.ResumeSyncEmail.id == sync_email_id
    ).first()
    
    if sync_email:
        logger.info(f"邮箱信息: ID={sync_email.id}, 邮箱={sync_email.email}")
        logger.info(f"同步状态: is_active={sync_email.is_active}, last_sync_time={sync_email.last_sync_time}")
    else:
        logger.error(f"找不到ID为{sync_email_id}的邮箱配置")
    
    # 调用服务层方法
    return service.create_keyword(
        db,
        sync_email_id,
        keyword_in,
        current_user.tenant_id,
        current_user.is_superuser
    )


@router.get(
    "/{sync_email_id}/keywords",
    response_model=List[schemas.JobKeyword],
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["resume_sync_email_read"]
            )
        )
    ]
)
def read_keywords(
    *,
    db: Session = Depends(deps.get_db),
    sync_email_id: int,
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """获取职位关键字列表"""
    # 调用服务层方法
    return service.get_keywords(
        db,
        sync_email_id,
        current_user.tenant_id,
        current_user.is_superuser
    )


@router.put(
    "/keywords/{keyword_id}",
    response_model=schemas.JobKeyword,
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["resume_sync_email_update"]
            )
        )
    ]
)
def update_keyword(
    *,
    db: Session = Depends(deps.get_db),
    keyword_id: int,
    keyword_in: schemas.JobKeywordUpdate,
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """更新职位关键字"""
    # 调用服务层方法
    return service.update_keyword(
        db,
        keyword_id,
        keyword_in,
        current_user.tenant_id,
        current_user.is_superuser
    )


@router.delete(
    "/keywords/{keyword_id}",
    response_model=schemas.ResponseMsg,
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["resume_sync_email_update"]
            )
        )
    ]
)
def delete_keyword(
    *,
    db: Session = Depends(deps.get_db),
    keyword_id: int,
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """删除职位关键字"""
    # 调用服务层方法
    return service.delete_keyword(
        db,
        keyword_id,
        current_user.tenant_id,
        current_user.is_superuser
    )


@router.post(
    "/{sync_email_id}/sync",
    response_model=schemas.ResponseMsg,
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["resume_sync_email_read"]
            )
        )
    ]
)
async def trigger_sync(
    *,
    db: Session = Depends(deps.get_db),
    sync_email_id: int,
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """手动触发邮箱同步"""
    # 添加日志记录
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(
        f"用户 {current_user.email} 触发了邮箱同步, "
        f"同步ID: {sync_email_id}"
    )
    
    # 获取邮箱配置
    sync_email = service.get_sync_email(
        db,
        sync_email_id,
        current_user.tenant_id,
        current_user.is_superuser
    )
    
    if sync_email:
        logger.info(f"找到邮箱配置: {sync_email.email}")
        logger.info(
            f"同步状态: 活跃={sync_email.is_active}, "
            f"上次同步={sync_email.last_sync_time}"
        )
    
    # 同步邮箱
    logger.info("开始执行邮箱同步...")
    await service.sync_emails(sync_email)
    logger.info("邮箱同步过程执行完毕")
    
    return {"message": "邮箱同步已完成"}


@router.post(
    "/test-connection",
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["resume_sync_email_create"]
            )
        )
    ]
)
async def test_email_connection(
    *,
    db: Session = Depends(deps.get_db),
    test_data: schemas.ResumeSyncEmailUpdate,
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """测试邮箱连接"""
    # 打印请求数据，帮助调试（不包含密码）
    import logging
    logger = logging.getLogger(__name__)
    
    safe_data = {k: v for k, v in test_data.dict().items() if k != 'password'}
    logger.info(f"收到测试连接请求: {safe_data}")
    
    # 调用服务层方法
    return await service.test_email_connection(test_data) 