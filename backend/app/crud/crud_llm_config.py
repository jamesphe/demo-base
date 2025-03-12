from typing import List, Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.llm_config import LLMConfig
from app.schemas.llm_config import LLMConfigCreate, LLMConfigUpdate


class CRUDLLMConfig(CRUDBase[LLMConfig, LLMConfigCreate, LLMConfigUpdate]):
    def get_by_name(self, db: Session, *, name: str) -> Optional[LLMConfig]:
        """根据名称获取配置"""
        return db.query(LLMConfig).filter(LLMConfig.name == name).first()
    
    def get_default(self, db: Session) -> Optional[LLMConfig]:
        """获取默认配置"""
        return db.query(LLMConfig).filter(LLMConfig.is_default == True).first()
    
    def get_enabled(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[LLMConfig]:
        """获取所有启用的配置"""
        return (
            db.query(LLMConfig)
            .filter(LLMConfig.is_enabled == True)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def set_default(self, db: Session, *, config_id: int) -> LLMConfig:
        """设置默认配置"""
        # 先取消其他默认配置
        db.query(LLMConfig).filter(LLMConfig.is_default == True).update(
            {"is_default": False}
        )
        # 设置新的默认配置
        config = self.get(db, id=config_id)
        if config:
            config.is_default = True
            db.add(config)
            db.commit()
            db.refresh(config)
        return config


llm_config = CRUDLLMConfig(LLMConfig) 