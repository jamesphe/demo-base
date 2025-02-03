# 导入所有模型，确保它们已注册到Base.metadata
from app.db.base_class import Base  # noqa: F401
from app.db.session import SessionLocal, engine  # noqa: F401

# 为了使alembic能够检测到所有模型，这些导入是必要的
__all__ = ["Base", "SessionLocal", "engine"]

# Import all models here for Alembic
from app.models import user, job, candidate, interview  # noqa: F401 