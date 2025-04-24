from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime
from sqlalchemy import and_, or_

from app import models, schemas, crud
from app.schemas.tenant import TenantCreate, TenantUpdate
from .base import BaseService
from app.schemas.user import UserCreate


class TenantService(BaseService[models.Tenant, TenantCreate, TenantUpdate]):
    """租户服务"""
    
    def __init__(self):
        super().__init__(models.Tenant)

    def get_by_code(
        self,
        db: Session,
        *,
        code: str
    ) -> Optional[models.Tenant]:
        """根据租户代码获取租户"""
        return db.query(models.Tenant).filter(
            models.Tenant.code == code
        ).first()

    def check_external_id_unique(
        self, 
        db: Session, 
        external_id: str, 
        exclude_id: Optional[int] = None
    ) -> None:
        """检查外部系统编号是否唯一"""
        if not external_id:
            return
            
        existing_tenant = crud.tenant.get_by_external_id(db, external_id=external_id)
        if existing_tenant and (exclude_id is None or existing_tenant.id != exclude_id):
            raise HTTPException(
                status_code=400,
                detail="外部系统编号已存在"
            )

    def check_tenant_name_unique(
        self, 
        db: Session, 
        tenant_name: str, 
        exclude_id: Optional[int] = None
    ) -> None:
        """检查租户名称是否唯一"""
        if not tenant_name:
            return
        
        existing_tenant = crud.tenant.get_by_name(db, tenant_name=tenant_name)
        if existing_tenant and (exclude_id is None or existing_tenant.id != exclude_id):
            raise HTTPException(
                status_code=400,
                detail="租户名称已存在"
            )

    def create_tenant(
        self, 
        db: Session, 
        tenant_in: TenantCreate
    ) -> models.Tenant:
        """创建租户"""
        # 检查租户名称唯一性
        self.check_tenant_name_unique(db, tenant_in.tenant_name)
        
        # 检查外部系统编号唯一性
        self.check_external_id_unique(db, tenant_in.external_id)
        
        # 将 camelCase 转换为 snake_case
        tenant_data = {
            "tenant_name": tenant_in.tenant_name,
            "contact_person": tenant_in.contact_person,
            "phone": tenant_in.phone,
            "email": tenant_in.email,
            "address": tenant_in.address,
            "external_id": tenant_in.external_id,
            "status": tenant_in.status
        }
        return crud.tenant.create(db=db, obj_in=tenant_data)

    async def create_default_configs(
        self,
        db: Session,
        *,
        tenant_id: int
    ) -> None:
        """创建租户的默认配置"""
        from app.services import llm_config_service
        
        # 创建默认LLM配置
        default_llm_config = {
            "name": "默认LLM配置",
            "provider": "openai",
            "api_key": "",
            "model_name": "gpt-3.5-turbo",
            "tenant_id": tenant_id,
            "is_default": True,
            "is_active": True
        }
        await llm_config_service.create_config(
            db,
            obj_in=schemas.LLMConfigCreate(**default_llm_config)
        )

    async def get_tenant_statistics(
        self,
        db: Session,
        *,
        tenant_id: int
    ) -> Dict[str, Any]:
        """获取租户统计信息"""
        tenant = self.get(db, id=tenant_id)
        if not tenant:
            raise HTTPException(status_code=404, detail="租户不存在")
            
        # 统计用户数量
        user_count = db.query(models.User).filter(
            models.User.tenant_id == tenant_id
        ).count()
        
        # 统计职位数量
        job_count = db.query(models.Job).filter(
            models.Job.tenant_id == tenant_id
        ).count()
        
        # 统计候选人数量
        candidate_count = db.query(models.Candidate).filter(
            models.Candidate.tenant_id == tenant_id
        ).count()
        
        # 统计简历数量
        resume_count = db.query(models.Resume).filter(
            models.Resume.tenant_id == tenant_id
        ).count()
        
        # 统计面试数量
        interview_count = db.query(models.Interview).filter(
            models.Interview.tenant_id == tenant_id
        ).count()
        
        return {
            "user_count": user_count,
            "job_count": job_count,
            "candidate_count": candidate_count,
            "resume_count": resume_count,
            "interview_count": interview_count,
            "created_at": tenant.created_at,
            "last_active": tenant.last_active
        }

    def update_tenant_status(
        self,
        db: Session,
        *,
        tenant_id: int,
        is_active: bool,
        note: Optional[str] = None
    ) -> models.Tenant:
        """更新租户状态"""
        tenant = self.get(db, id=tenant_id)
        if not tenant:
            raise HTTPException(status_code=404, detail="租户不存在")
            
        # 创建状态变更记录
        status_change = models.TenantStatusChange(
            tenant_id=tenant_id,
            from_status=tenant.is_active,
            to_status=is_active,
            note=note,
            created_at=datetime.utcnow()
        )
        db.add(status_change)
        
        # 更新租户状态
        tenant = self.update(
            db,
            db_obj=tenant,
            obj_in=TenantUpdate(
                is_active=is_active,
                last_active=datetime.utcnow() if is_active else tenant.last_active
            )
        )
        
        return tenant

    def get_status_history(
        self,
        db: Session,
        *,
        tenant_id: int
    ) -> List[Dict[str, Any]]:
        """获取租户状态变更历史"""
        history = db.query(models.TenantStatusChange).filter(
            models.TenantStatusChange.tenant_id == tenant_id
        ).order_by(
            models.TenantStatusChange.created_at.desc()
        ).all()
        
        return [
            {
                "from_status": h.from_status,
                "to_status": h.to_status,
                "note": h.note,
                "created_at": h.created_at
            }
            for h in history
        ]

    def update_tenant(
        self, 
        db: Session, 
        tenant: models.Tenant, 
        tenant_in: TenantUpdate
    ) -> models.Tenant:
        """更新租户"""
        if isinstance(tenant_in, dict):
            update_data = tenant_in
        else:
            update_data = tenant_in.model_dump(exclude_unset=True)
        
        # 检查租户名称唯一性
        if "tenant_name" in update_data:
            self.check_tenant_name_unique(
                db, 
                update_data["tenant_name"], 
                exclude_id=tenant.id
            )
        
        # 检查外部系统编号唯一性
        if "external_id" in update_data:
            self.check_external_id_unique(
                db, 
                update_data["external_id"], 
                exclude_id=tenant.id
            )
        
        # 将 camelCase 转换为 snake_case
        tenant_data = {
            "tenant_name": update_data["tenant_name"],
            "contact_person": update_data["contact_person"],
            "phone": update_data["phone"],
            "email": update_data["email"],
            "address": update_data["address"],
            "external_id": update_data["external_id"],
            "status": update_data["status"]
        }
        return crud.tenant.update(
            db=db,
            db_obj=tenant,
            obj_in=tenant_data
        )


# 创建服务实例
tenant_service = TenantService()

# 只导出实例
__all__ = ["tenant_service"]

def process_tenant_id(db: Session, user_in: schemas.UserCreate) -> Optional[int]:
    """
    处理用户创建时的租户ID关联
    """
    # 如果是candidate类型用户,不关联租户
    if user_in.user_type == 'candidate':
        return None
        
    # 如果是admin类型用户且未指定租户,不关联租户
    if user_in.user_type == 'admin' and not user_in.tenant_id:
        return None
        
    # 如果是tenant类型用户,必须关联租户
    if user_in.user_type == 'tenant':
        if not user_in.tenant_id and not user_in.external_tenant_id:
            raise HTTPException(
                status_code=400,
                detail="租户用户必须关联到一个租户"
            )
            
        # 如果提供了external_tenant_id,查找对应的tenant_id
        if user_in.external_tenant_id:
            tenant = crud.tenant.get_by_external_id(
                db, 
                external_id=user_in.external_tenant_id
            )
            if not tenant:
                raise HTTPException(
                    status_code=404,
                    detail=f"未找到外部租户ID为 {user_in.external_tenant_id} 的租户"
                )
            return tenant.id
           
    # 如果提供了tenant_id，则直接需要先检查是否存在
    if user_in.tenant_id:
        tenant = crud.tenant.get(db, id=user_in.tenant_id)
        if not tenant:
            raise HTTPException(
                status_code=404,
                detail=f"未找到内部租户ID为 {user_in.tenant_id} 的租户"
            )
        return tenant.id

    return user_in.tenant_id if user_in.tenant_id else None

# 添加独立的create_tenant函数，用于企业微信授权
def create_tenant(db: Session, tenant_data: Dict[str, Any]) -> models.Tenant:
    """
    创建租户（用于企业微信授权）
    
    Args:
        db: 数据库会话
        tenant_data: 租户数据
        
    Returns:
        models.Tenant: 创建的租户对象
    """
    # 创建租户
    tenant = models.Tenant(**tenant_data)
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return tenant