from fastapi import APIRouter
from app.api.api_v1.endpoints import (
    auth, users, jobs, candidates, interviews,
    resumes, repositories, roles, permissions,
    tenants, llm_configs, talents, skills,
    certifications, educations, experiences,
    talent_pools
)

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

# 职位管理
api_router.include_router(
    jobs.router, 
    prefix="/jobs", 
    tags=["职位管理"]
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

# 技能管理
api_router.include_router(
    skills.router, 
    prefix="/skills", 
    tags=["技能管理"]
)

# 人才相关信息管理
api_router.include_router(
    certifications.router,
    prefix="/certifications",
    tags=["认证管理"]
)

api_router.include_router(
    educations.router,
    prefix="/educations",
    tags=["教育经历"]
)

api_router.include_router(
    experiences.router,
    prefix="/experiences",
    tags=["工作经验"]
)

# 人才库管理
api_router.include_router(
    talent_pools.router,
    prefix="/talent-pools",
    tags=["人才库管理"]
) 