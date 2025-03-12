from typing import List, Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.permission import Permission
from app.schemas.permission import PermissionCreate, PermissionUpdate


class CRUDPermission(CRUDBase[Permission, PermissionCreate, PermissionUpdate]):
    def get_by_name(
        self, 
        db: Session, 
        *, 
        name: str
    ) -> Optional[Permission]:
        return (
            db.query(Permission)
            .filter(Permission.name == name)
            .first()
        )

    def get_role_permissions(
        self, 
        db: Session, 
        *, 
        role_id: int
    ) -> List[Permission]:
        """获取角色的所有权限"""
        return (
            db.query(Permission)
            .join(Permission.roles)
            .filter(Permission.roles.any(id=role_id))
            .all()
        )


permission = CRUDPermission(Permission) 