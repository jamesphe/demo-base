from typing import List, Dict, Any, Optional, Set
from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime
from sqlalchemy import and_, or_

from app import models, schemas
from app.schemas.permission import PermissionCreate, PermissionUpdate
from app.schemas.role import RoleCreate, RoleUpdate
from .base import BaseService


class PermissionService(BaseService[models.Permission, PermissionCreate, PermissionUpdate]):
    """权限服务"""
    
    def __init__(self):
        super().__init__(models.Permission)

    def get_by_code(
        self,
        db: Session,
        *,
        code: str
    ) -> Optional[models.Permission]:
        """根据权限代码获取权限"""
        return db.query(models.Permission).filter(
            models.Permission.code == code
        ).first()

    def create_permission(
        self,
        db: Session,
        *,
        obj_in: PermissionCreate
    ) -> models.Permission:
        """创建权限"""
        # 检查权限代码是否已存在
        existing = self.get_by_code(db, code=obj_in.code)
        if existing:
            raise HTTPException(
                status_code=400,
                detail="权限代码已存在"
            )
            
        return self.create(db=db, obj_in=obj_in)

    def get_role_permissions(
        self,
        db: Session,
        *,
        role_id: int
    ) -> List[models.Permission]:
        """获取角色的权限列表"""
        role = db.query(models.Role).get(role_id)
        if not role:
            raise HTTPException(status_code=404, detail="角色不存在")
            
        return role.permissions

    def update_role_permissions(
        self,
        db: Session,
        *,
        role_id: int,
        permission_ids: List[int]
    ) -> models.Role:
        """更新角色的权限"""
        role = db.query(models.Role).get(role_id)
        if not role:
            raise HTTPException(status_code=404, detail="角色不存在")
            
        # 验证权限是否存在
        permissions = db.query(models.Permission).filter(
            models.Permission.id.in_(permission_ids)
        ).all()
        if len(permissions) != len(permission_ids):
            raise HTTPException(status_code=400, detail="存在无效的权限ID")
            
        # 更新角色权限
        role.permissions = permissions
        db.add(role)
        db.commit()
        db.refresh(role)
        
        return role

    def get_user_permissions(
        self,
        db: Session,
        *,
        user_id: int
    ) -> Set[str]:
        """获取用户的所有权限代码"""
        user = db.query(models.User).get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
            
        permission_codes = set()
        for role in user.roles:
            for permission in role.permissions:
                permission_codes.add(permission.code)
                
        return permission_codes

    def check_permission(
        self,
        db: Session,
        *,
        user_id: int,
        permission_code: str
    ) -> bool:
        """检查用户是否有指定权限"""
        user = db.query(models.User).get(user_id)
        if not user:
            return False
            
        # 超级管理员拥有所有权限
        if user.is_superuser:
            return True
            
        # 检查用户权限
        user_permissions = self.get_user_permissions(db, user_id=user_id)
        return permission_code in user_permissions

    def get_permission_tree(
        self,
        db: Session
    ) -> List[Dict[str, Any]]:
        """获取权限树结构"""
        permissions = db.query(models.Permission).all()
        
        # 构建权限树
        permission_tree = {}
        for permission in permissions:
            module = permission.module
            if module not in permission_tree:
                permission_tree[module] = {
                    "module": module,
                    "permissions": []
                }
            permission_tree[module]["permissions"].append({
                "id": permission.id,
                "code": permission.code,
                "name": permission.name,
                "description": permission.description
            })
            
        return list(permission_tree.values())


# 创建服务实例
permission_service = PermissionService()

# 只导出实例
__all__ = ["permission_service"] 