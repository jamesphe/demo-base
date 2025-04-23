from fastapi import APIRouter

from app.api.endpoints import users, auth, candidates, jobs, resumes, tenants, interviews, applications

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(users.router, prefix="/users", tags=["用户"])
api_router.include_router(tenants.router, prefix="/tenants", tags=["租户"])
api_router.include_router(candidates.router, prefix="/candidates", tags=["候选人"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["职位"])
api_router.include_router(resumes.router, prefix="/resumes", tags=["简历"])
api_router.include_router(interviews.router, prefix="/interviews", tags=["面试"])
api_router.include_router(applications.router, prefix="/applications", tags=["职位申请"]) 