from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from fastapi import HTTPException
from datetime import datetime

from app import crud, models, schemas
from app.core.config import settings
from app.core.llm import validate_llm_connection
from app.schemas.llm_config import LLMConfigCreate, LLMConfigUpdate
from .base import BaseService


class LLMConfigService(BaseService[models.LLMConfig, LLMConfigCreate, LLMConfigUpdate]):
    """LLM配置服务"""
    
    def __init__(self):
        super().__init__(models.LLMConfig)

    def get_configs(
        self,
        db: Session,
        *,
        tenant_id: Optional[int] = None,
        is_active: bool = True,
        skip: int = 0,
        limit: int = 100
    ) -> List[models.LLMConfig]:
        """获取LLM配置列表"""
        query = db.query(models.LLMConfig)
        
        if tenant_id is not None:
            query = query.filter(models.LLMConfig.tenant_id == tenant_id)
        if is_active:
            query = query.filter(models.LLMConfig.is_active == True)
            
        return query.offset(skip).limit(limit).all()

    def get_config_by_name(
        self,
        db: Session,
        *,
        name: str,
        tenant_id: Optional[int] = None
    ) -> Optional[models.LLMConfig]:
        """根据名称获取LLM配置"""
        query = db.query(models.LLMConfig).filter(
            models.LLMConfig.name == name
        )
        
        if tenant_id is not None:
            query = query.filter(models.LLMConfig.tenant_id == tenant_id)
            
        return query.first()

    async def create_config(
        self,
        db: Session,
        *,
        obj_in: LLMConfigCreate
    ) -> models.LLMConfig:
        """创建LLM配置"""
        # 检查名称是否已存在
        existing = self.get_config_by_name(
            db,
            name=obj_in.name,
            tenant_id=obj_in.tenant_id
        )
        if existing:
            raise HTTPException(
                status_code=400,
                detail="配置名称已存在"
            )
            
        # 如果设置为默认配置,需要取消其他默认配置
        if obj_in.is_default:
            self.clear_default_config(db, tenant_id=obj_in.tenant_id)
            
        # 验证连接
        if obj_in.validate_connection:
            try:
                await validate_llm_connection(obj_in.dict())
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"LLM连接验证失败: {str(e)}"
                )
                
        return super().create(db, obj_in=obj_in)

    def update_config(
        self,
        db: Session,
        *,
        config_id: int,
        obj_in: LLMConfigUpdate
    ) -> models.LLMConfig:
        """更新LLM配置"""
        config = self.get(db, id=config_id)
        if not config:
            raise HTTPException(status_code=404, detail="配置不存在")
            
        # 检查名称是否已被其他配置使用
        if obj_in.name and obj_in.name != config.name:
            existing = self.get_config_by_name(
                db,
                name=obj_in.name,
                tenant_id=config.tenant_id
            )
            if existing:
                raise HTTPException(
                    status_code=400,
                    detail="配置名称已存在"
                )
                
        # 如果设置为默认配置,需要取消其他默认配置
        if obj_in.is_default:
            self.clear_default_config(db, tenant_id=config.tenant_id)
            
        return super().update(db, db_obj=config, obj_in=obj_in)

    def clear_default_config(
        self,
        db: Session,
        *,
        tenant_id: int
    ) -> None:
        """清除租户的默认配置"""
        db.query(models.LLMConfig).filter(
            and_(
                models.LLMConfig.tenant_id == tenant_id,
                models.LLMConfig.is_default == True
            )
        ).update({"is_default": False})
        db.commit()

    def get_default_config(
        self,
        db: Session
    ) -> Optional[models.LLMConfig]:
        """获取默认LLM配置(超级管理员)"""
        return db.query(models.LLMConfig).filter(
            models.LLMConfig.is_default == True
        ).first()

    def get_default_config_by_tenant(
        self,
        db: Session,
        *,
        tenant_id: int
    ) -> Optional[models.LLMConfig]:
        """获取租户的默认LLM配置"""
        return db.query(models.LLMConfig).filter(
            and_(
                models.LLMConfig.tenant_id == tenant_id,
                models.LLMConfig.is_default == True
            )
        ).first()

    async def validate_config(
        self,
        db: Session,
        *,
        config_id: int
    ) -> Dict[str, Any]:
        """验证LLM配置"""
        config = self.get(db, id=config_id)
        if not config:
            raise HTTPException(status_code=404, detail="配置不存在")
            
        try:
            await validate_llm_connection(config.dict())
            return {
                "status": "success",
                "message": "连接验证成功"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"连接验证失败: {str(e)}"
            }


# 创建服务实例
llm_config_service = LLMConfigService()

# 只导出实例
__all__ = ["llm_config_service"] 