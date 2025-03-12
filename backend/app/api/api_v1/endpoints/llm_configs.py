from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.api import deps
from app.services import llm_config_service

router = APIRouter()


@router.get(
    "/",
    response_model=List[schemas.LLMConfig],
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["llm_config_read"]
            )
        )
    ]
)
def read_llm_configs(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """获取LLM配置列表"""
    if current_user.is_superuser:
        configs = llm_config_service.get_configs(db, skip=skip, limit=limit)
    else:
        configs = llm_config_service.get_configs_by_tenant(
            db,
            tenant_id=current_user.tenant_id,
            skip=skip,
            limit=limit
        )
    return configs


@router.post(
    "/",
    response_model=schemas.LLMConfig,
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["llm_config_create"]
            )
        )
    ]
)
def create_llm_config(
    *,
    db: Session = Depends(deps.get_db),
    config_in: schemas.LLMConfigCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """创建新的LLM配置"""
    # 检查配置名称是否已存在
    if llm_config_service.get_config_by_name(db, name=config_in.name):
        raise HTTPException(
            status_code=400,
            detail="该配置名称已存在"
        )
    
    # 创建配置并关联到当前租户
    config = llm_config_service.create_config(
        db=db,
        config_in=config_in,
        tenant_id=current_user.tenant_id
    )
    return config


@router.get(
    "/{config_id}",
    response_model=schemas.LLMConfig,
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["llm_config_read"]
            )
        )
    ]
)
def read_llm_config(
    *,
    db: Session = Depends(deps.get_db),
    config_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """获取指定LLM配置"""
    config = llm_config_service.get_config(db, id=config_id)
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    # 检查租户权限
    if not current_user.is_superuser and config.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="无权访问该配置")
    
    return config


@router.put(
    "/{config_id}",
    response_model=schemas.LLMConfig,
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["llm_config_update"]
            )
        )
    ]
)
def update_llm_config(
    *,
    db: Session = Depends(deps.get_db),
    config_id: int,
    config_in: schemas.LLMConfigUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """更新LLM配置"""
    config = llm_config_service.get_config(db, id=config_id)
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    # 检查租户权限
    if not current_user.is_superuser and config.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="无权更新该配置")
    
    config = llm_config_service.update_config(
        db=db,
        config=config,
        config_in=config_in
    )
    return config


@router.delete(
    "/{config_id}",
    response_model=schemas.LLMConfig,
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["llm_config_delete"]
            )
        )
    ]
)
def delete_llm_config(
    *,
    db: Session = Depends(deps.get_db),
    config_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """删除LLM配置"""
    config = llm_config_service.get_config(db, id=config_id)
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    # 检查租户权限
    if not current_user.is_superuser and config.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="无权删除该配置")
    
    # 检查是否为默认配置
    if config.is_default:
        raise HTTPException(
            status_code=400,
            detail="不能删除默认配置"
        )
    
    config = llm_config_service.delete_config(db=db, id=config_id)
    return config


@router.post(
    "/{config_id}/set-default",
    response_model=schemas.LLMConfig,
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["llm_config_update"]
            )
        )
    ]
)
def set_default_config(
    *,
    db: Session = Depends(deps.get_db),
    config_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """设置默认LLM配置"""
    config = llm_config_service.get_config(db, id=config_id)
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    # 检查租户权限
    if not current_user.is_superuser and config.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="无权设置该配置为默认")
    
    config = llm_config_service.set_default(db=db, config_id=config_id)
    return config


@router.get(
    "/default",
    response_model=schemas.LLMConfig,
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["llm_config_read"]
            )
        )
    ]
)
def get_default_config(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """获取默认LLM配置"""
    if current_user.is_superuser:
        config = llm_config_service.get_default_config(db)
    else:
        config = llm_config_service.get_default_config_by_tenant(
            db,
            tenant_id=current_user.tenant_id
        )
    
    if not config:
        raise HTTPException(status_code=404, detail="未设置默认配置")
    
    return config


@router.post(
    "/{config_id}/validate",
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["llm_config_validate"]
            )
        )
    ]
)
def validate_config(
    *,
    db: Session = Depends(deps.get_db),
    config_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """验证LLM配置是否有效"""
    config = llm_config_service.get_config(db, id=config_id)
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    # 检查租户权限
    if not current_user.is_superuser and config.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="无权验证该配置")
    
    try:
        llm_config_service.validate_config(db=db, config_id=config_id)
        return {"message": "配置有效"}
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"配置无效: {str(e)}"
        ) 