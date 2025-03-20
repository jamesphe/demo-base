from typing import Optional
from sqlalchemy.orm import Session
from app import models

class CRUDSkill:
    def get_by_name(self, db: Session, *, name: str) -> Optional[models.Skill]:
        return db.query(self.model).filter(self.model.name == name).first() 