from sqlalchemy import Column, Integer, ForeignKey
from app.db.base_class import Base


class RolePermission(Base):
    """角色-权限关联模型"""
    
    __tablename__ = "role_permission"
    
    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("role.id"))
    permission_id = Column(Integer, ForeignKey("permission.id")) 