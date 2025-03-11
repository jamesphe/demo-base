from fastapi import APIRouter
from app.api.api_v1.endpoints import (
    login, users, jobs, candidates, resumes, repositories
)

api_router = APIRouter()

api_router.include_router(login.router, tags=["登录"])
api_router.include_router(users.router, prefix="/users", tags=["用户"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["职位"])
api_router.include_router(
    candidates.router, 
    prefix="/candidates", 
    tags=["候选人"]
)
api_router.include_router(
    resumes.router,
    prefix="/resumes",
    tags=["简历"]
)
api_router.include_router(
    repositories.router,
    prefix="/repositories",
    tags=["简历库"]
) 