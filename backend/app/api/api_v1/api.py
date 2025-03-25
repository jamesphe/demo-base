from fastapi import APIRouter
from app.api.api_v1.endpoints import (
    auth, users, jobs, candidates, interviews,
    resumes, repositories, roles, permissions,
    tenants, llm_configs, talents, skills,
    talent_pools, talent_certifications, certifications,
    talent_educations, talent_experiences, resume_reviews,
    job_applications
)
from app.api.api_v1.endpoints import trial_application

api_router = APIRouter()

# 认证相关
api_router.include_router(auth.router, tags=["认证"])

# 用户管理
api_router.include_router(
    users.router, 
    prefix="/users", 
    tags=["用户管理"]
)

# 租户管理
api_router.include_router(
    tenants.router,
    prefix="/tenants",
    tags=["租户管理"]
)

# 角色权限
api_router.include_router(
    roles.router,
    prefix="/roles",
    tags=["角色管理"]
)

api_router.include_router(
    permissions.router,
    prefix="/permissions", 
    tags=["权限管理"]
)

# 技能管理
api_router.include_router(
    skills.router, 
    prefix="/skills", 
    tags=["技能管理"]
)

# 证书库管理
api_router.include_router(
    certifications.router,
    prefix="/certifications", 
    tags=["证书类型库管理"]
) 

# 职位管理
api_router.include_router(
    jobs.router, 
    prefix="/jobs", 
    tags=["职位管理"]
)

# 简历管理
api_router.include_router(
    repositories.router,
    prefix="/repositories",
    tags=["简历库管理"]
)

api_router.include_router(
    resumes.router,
    prefix="/resumes",
    tags=["简历管理"]
)

api_router.include_router(
    resume_reviews.router,
    prefix="/resume-reviews",
    tags=["简历审核"]
)

# 候选人管理
api_router.include_router(
    candidates.router, 
    prefix="/candidates", 
    tags=["候选人管理"]
)

# 面试管理
api_router.include_router(
    interviews.router,
    prefix="/interviews",
    tags=["面试管理"]
)

# 系统配置
api_router.include_router(
    llm_configs.router,
    prefix="/llm-configs",
    tags=["LLM配置"]
)

# 人才管理
api_router.include_router(
    talents.router, 
    prefix="/talents", 
    tags=["人才管理"]
)

# 人才相关信息管理
api_router.include_router(
    talent_certifications.router,
    prefix="/talent-certifications",
    tags=["人才认证管理"]
)

api_router.include_router(
    talent_educations.router,
    prefix="/talent-educations",
    tags=["人才教育经历"]
)

api_router.include_router(
    talent_experiences.router,
    prefix="/talent-experiences",
    tags=["人才工作经验"]
)

# 人才库管理
api_router.include_router(
    talent_pools.router,
    prefix="/talent-pools",
    tags=["人才库管理"]
)

# 职位申请全局管理
api_router.include_router(
    job_applications.router, 
    prefix="/job-applications", 
    tags=["职位申请管理"]
)

# 试用相关
api_router.include_router(
    trial_application.router,
    prefix="/user/trial",
    tags=["试用管理"]
)
