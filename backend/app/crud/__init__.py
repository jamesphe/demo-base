from .crud_user import user
from .crud_job import job
from .crud_candidate import candidate
from .crud_interview import interview
from .crud_resume import resume
from .crud_resume_repository import repository
from .crud_role import role
from .crud_permission import permission
from .crud_tenant import tenant
from .crud_llm_config import llm_config
# ... 其他crud导入

# 直接导出所有crud操作
crud = {
    "user": user,
    "job": job,
    "candidate": candidate,
    "interview": interview,
    "resume": resume,
    "repository": repository,
    "role": role,
    "permission": permission,
    "tenant": tenant,
    "llm_config": llm_config
}

__all__ = ["crud"]