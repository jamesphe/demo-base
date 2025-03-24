from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base_class import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenant.id"), nullable=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(255), unique=True, index=True, nullable=False)
    user_type = Column(Enum('candidate', 'tenant', 'admin', name='user_type'), nullable=False, default='tenant')
    hashed_password = Column(String(255), nullable=False)
    avatar = Column(String(255))
    introduction = Column(String(255))
    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow
    )

    # 关联关系
    tenant = relationship("Tenant", back_populates="users")
    interviews = relationship("Interview", back_populates="interviewer")
    roles = relationship(
        "Role",
        secondary="user_role",
        back_populates="users",
        primaryjoin="user_role.c.user_id == User.id",
        secondaryjoin="user_role.c.role_id == Role.id"
    )
    notifications = relationship("Notification", back_populates="user")
    published_jobs = relationship(
        "Job",
        back_populates="publisher",
        foreign_keys="[Job.publisher_id]"
    )

    def has_permission(self, permission_name: str) -> bool:
        """检查用户是否拥有指定权限"""
        # 超级管理员拥有所有权限
        if self.is_superuser:
            return True
            
        for role in self.roles:
            for permission in role.permissions:
                if permission.name == permission_name:
                    return True
        return False

    def get_roles(self) -> list:
        """获取用户角色列表"""
        # 超级管理员可能需要特殊处理
        if self.is_superuser:
            return ["admin"] + [role.name for role in self.roles]
        
        # 返回用户实际分配的角色名称
        return [role.name for role in self.roles] 