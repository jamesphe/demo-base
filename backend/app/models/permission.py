from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Permission(Base):
    __tablename__ = "permission"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(255))
    
    # 关联
    roles = relationship(
        "Role",
        secondary="role_permission",
        back_populates="permissions"
    ) 