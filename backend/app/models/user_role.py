from sqlalchemy import Column, Integer, ForeignKey
from app.db.base_class import Base

class UserRole(Base):
    __tablename__ = "user_role"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    role_id = Column(Integer, ForeignKey("role.id")) 