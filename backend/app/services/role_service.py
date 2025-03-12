from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime
from sqlalchemy import and_, or_

from app import models, schemas
from app.schemas.role import RoleCreate, RoleUpdate
from .base import BaseService


class RoleService(BaseService[models.Role, RoleCreate, RoleUpdate]):
    """角色服务"""
    
    def __init__(self):
        super().__init__(models.Role)

    def get_by_code(
        self,
        db: Session,
        *,
        code: str,
        tenant_id: Optional[int] = None
    ) -> Optional[models.Role]:
        """根据角色代码获取角色"""
        query = db.query(models.Role).filter(models.Role.code == code)
        if tenant_id is not None:
            query = query.filter(models.Role.tenant_id == tenant_id)
        return query.first()

    def create_role(
        self,
        db: Session,
        *,
        obj_in: RoleCreate
    ) -> models.Role:
        """创建角色"""
        # 检查角色代码是否已存在
        existing = self.get_by_code(
            db,
            code=obj_in.code,
            tenant_id=obj_in.tenant_id
        )
        if existing:
            raise HTTPException(
                status_code=400,
                detail="角色代码已存在"
            )
            
        return self.create(db=db, obj_in=obj_in)

    def get_user_roles(
        self,
        db: Session,
        *,
        user_id: int
    ) -> List[models.Role]:
        """获取用户的角色列表"""
        user = db.query(models.User).get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
            
        return user.roles

    def update_user_roles(
        self,
        db: Session,
        *,
        user_id: int,
        role_ids: List[int]
    ) -> models.User:
        """更新用户的角色"""
        user = db.query(models.User).get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
            
        # 验证角色是否存在
        roles = db.query(models.Role).filter(
            models.Role.id.in_(role_ids)
        ).all()
        if len(roles) != len(role_ids):
            raise HTTPException(status_code=400, detail="存在无效的角色ID")
            
        # 验证角色是否属于同一租户
        for role in roles:
            if role.tenant_id != user.tenant_id:
                raise HTTPException(
                    status_code=400,
                    detail="不能分配其他租户的角色"
                )
                
        # 更新用户角色
        user.roles = roles
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return user

    def get_tenant_roles(
        self,
        db: Session,
        *,
        tenant_id: int
    ) -> List[Dict[str, Any]]:
        """获取租户的角色列表"""
        roles = self.get_multi_by_tenant(db, tenant_id=tenant_id)
        
        result = []
        for role in roles:
            # 获取角色用户数量
            user_count = db.query(models.user_role).filter(
                models.user_role.c.role_id == role.id
            ).count()
            
            # 获取角色权限数量
            permission_count = db.query(models.role_permission).filter(
                models.role_permission.c.role_id == role.id
            ).count()
            
            result.append({
                "id": role.id,
                "code": role.code,
                "name": role.name,
                "description": role.description,
                "user_count": user_count,
                "permission_count": permission_count,
                "created_at": role.created_at
            })
            
        return result

    def get_role_users(
        self,
        db: Session,
        *,
        role_id: int
    ) -> List[Dict[str, Any]]:
        """获取角色的用户列表"""
        role = self.get(db, id=role_id)
        if not role:
            raise HTTPException(status_code=404, detail="角色不存在")
            
        users = []
        for user in role.users:
            users.append({
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "is_active": user.is_active,
                "created_at": user.created_at
            })
            
        return users

    def clone_role(
        self,
        db: Session,
        *,
        source_id: int,
        new_code: str,
        new_name: str,
        tenant_id: Optional[int] = None
    ) -> models.Role:
        """克隆角色"""
        # 获取源角色
        source_role = self.get(db, id=source_id)
        if not source_role:
            raise HTTPException(status_code=404, detail="源角色不存在")
            
        # 检查新角色代码
        if self.get_by_code(db, code=new_code, tenant_id=tenant_id):
            raise HTTPException(
                status_code=400,
                detail="角色代码已存在"
            )
            
        # 创建新角色
        new_role = self.create(
            db,
            obj_in=RoleCreate(
                code=new_code,
                name=new_name,
                description=f"从 {source_role.name} 克隆",
                tenant_id=tenant_id or source_role.tenant_id
            )
        )
        
        # 复制权限
        new_role.permissions = source_role.permissions
        db.add(new_role)
        db.commit()
        db.refresh(new_role)
        
        return new_role


# 创建服务实例
role_service = RoleService()

# 只导出实例
__all__ = ["role_service"] 