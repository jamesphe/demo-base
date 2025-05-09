from typing import List, Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.role import Role
from app.schemas.role import RoleCreate, RoleUpdate


class CRUDRole(CRUDBase[Role, RoleCreate, RoleUpdate]):
    def get_by_name(self, db: Session, *, name: str) -> Optional[Role]:
        return db.query(Role).filter(Role.name == name).first()

    def get_user_roles(
        self, 
        db: Session, 
        *, 
        user_id: int
    ) -> List[Role]:
        """获取用户的所有角色"""
        return (
            db.query(Role)
            .join(Role.users)
            .filter(Role.users.any(id=user_id))
            .all()
        )

    def count(self, db: Session) -> int:
        """获取角色总数"""
        return db.query(Role).count()


role = CRUDRole(Role)


# 只导出实例
__all__ = ["role"] 