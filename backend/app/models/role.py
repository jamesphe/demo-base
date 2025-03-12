from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class Role(Base):
    __tablename__ = "role"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255))
    
    # 修改关系定义，确保表名正确
    users = relationship(
        "User", 
        secondary="user_role",
        back_populates="roles",
        primaryjoin="user_role.c.role_id == Role.id",
        secondaryjoin="user_role.c.user_id == User.id"
    )
    permissions = relationship(
        "Permission", 
        secondary="role_permission",
        back_populates="roles"
    ) 