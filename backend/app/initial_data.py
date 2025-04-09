import logging
from sqlalchemy.orm import Session

from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.crud import crud
from app.core.config import settings
from app.schemas.tenant import TenantCreate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init() -> None:
    db = SessionLocal()
    try:
        logger.info("创建初始数据")
        init_db(db)
        init_tenants(db)  # 先初始化租户
        init_permissions(db)  # 再初始化权限
    finally:
        db.close()


def init_permissions(db: Session) -> None:
    """初始化权限数据"""
    permissions = [
        {"name": "candidate_read", "description": "查看候选人"},
        {"name": "candidate_create", "description": "创建候选人"},
        {"name": "candidate_update", "description": "更新候选人"},
        {"name": "candidate_delete", "description": "删除候选人"},
        {"name": "job_read", "description": "查看职位"},
        {"name": "job_create", "description": "创建职位"},
        {"name": "job_update", "description": "更新职位"},
        {"name": "job_delete", "description": "删除职位"},
        {"name": "tenant_read", "description": "查看租户"},
        {"name": "tenant_create", "description": "创建租户"},
        {"name": "tenant_update", "description": "更新租户"},
        {"name": "tenant_delete", "description": "删除租户"},
        {"name": "user_read", "description": "查看用户"},
        {"name": "user_create", "description": "创建用户"},
        {"name": "user_update", "description": "更新用户"},
        {"name": "user_delete", "description": "删除用户"},
        {"name": "role_read", "description": "查看角色"},
        {"name": "role_create", "description": "创建角色"},
        {"name": "role_update", "description": "更新角色"},
        {"name": "role_delete", "description": "删除角色"},
        {"name": "interview_read", "description": "查看面试"},
        {"name": "interview_create", "description": "创建面试"},
        {"name": "interview_update", "description": "更新面试"},
        {"name": "interview_delete", "description": "删除面试"},
        {"name": "job_application_read", "description": "查看职位申请"},
        {"name": "job_application_create", "description": "创建职位申请"},
        {"name": "job_application_update", "description": "更新职位申请"},
        {"name": "job_application_delete", "description": "删除职位申请"},
        {"name": "resume_read", "description": "查看简历"},
        {"name": "resume_create", "description": "创建简历"},
        {"name": "resume_update", "description": "更新简历"},
        {"name": "resume_delete", "description": "删除简历"},
        {"name": "resume_parse", "description": "解析简历"},
        {"name": "resume_review_read", "description": "查看简历评审"},
        {"name": "resume_review_update", "description": "更新简历评审"},
        {"name": "repository_read", "description": "查看仓库"},
        {"name": "repository_create", "description": "创建仓库"},
        {"name": "repository_delete", "description": "删除仓库"},
        {"name": "llm_config_read", "description": "查看LLM配置"},
        {"name": "llm_config_create", "description": "创建LLM配置"},
        {"name": "llm_config_update", "description": "更新LLM配置"},
        {"name": "llm_config_delete", "description": "删除LLM配置"},
        {"name": "llm_config_validate", "description": "验证LLM配置"}
    ]
    
    roles = [
        {
            "name": "admin",
            "description": "管理员",
            "permissions": ["*"]  # 所有权限
        },
        {
            "name": "hr",
            "description": "人力资源",
            "permissions": [
                "candidate_read",
                "candidate_create",
                "candidate_update",
                "job_read",
                "job_create",
                "job_application_read",
                "job_application_update",
                "resume_read",
                "resume_review_read",
                "resume_review_update"
            ]
        },
        {
            "name": "interviewer",
            "description": "面试官",
            "permissions": [
                "candidate_read",
                "interview_read",
                "interview_create",
                "interview_update",
                "resume_read",
                "job_application_read"
            ]
        },
        {
            "name": "tenant_admin",
            "description": "租户管理员",
            "permissions": [
                "candidate_read",
                "candidate_create",
                "candidate_update",
                "candidate_delete",
                "job_read",
                "job_create",
                "job_update",
                "job_delete",
                "interview_read",
                "interview_create",
                "interview_update",
                "interview_delete",
                "user_read",
                "user_create",
                "user_update",
                "user_delete",
                "role_read",
                "role_create",
                "role_update",
                "role_delete",
                "tenant_read",
                "tenant_create",
                "tenant_update",
                "tenant_delete",
                "job_application_read",
                "job_application_create",
                "job_application_update",
                "job_application_delete",
                "resume_read",
                "resume_create",
                "resume_update",
                "resume_delete",
                "resume_parse",
                "resume_review_read",
                "resume_review_update",
                "repository_read",
                "repository_create",
                "repository_delete",
                "llm_config_read",
                "llm_config_create",
                "llm_config_update",
                "llm_config_delete",
                "llm_config_validate"
            ]
        },
        {
            "name": "tenant_user",
            "description": "租户用户",
            "permissions": [
                "candidate_read",
                "job_read",
                "interview_read",
                "user_read",
                "role_read",
                "tenant_read",
                "job_application_read",
                "resume_read",
                "resume_review_read",
                "repository_read",
                "llm_config_read"
            ]
        }
    ]
    
    # 创建权限
    for perm in permissions:
        db_perm = crud["permission"].get_by_name(db, name=perm["name"])
        if not db_perm:
            crud["permission"].create(db, obj_in=perm)
            
    # 创建角色和关联权限
    for role in roles:
        db_role = crud["role"].get_by_name(db, name=role["name"])
        if not db_role:
            role_perms = role.pop("permissions")
            db_role = crud["role"].create(db, obj_in=role)
            
            # 关联权限
            if "*" in role_perms:
                # 管理员获得所有权限
                all_perms = crud["permission"].get_multi(db)
                db_role.permissions.extend(all_perms)
            else:
                for perm_name in role_perms:
                    perm = crud["permission"].get_by_name(db, name=perm_name)
                    if perm:
                        db_role.permissions.append(perm)
            
            db.add(db_role)
            db.commit()


def init_tenants(db: Session) -> None:
    """初始化租户数据"""
    tenants = [
        {
            "tenant_name": "示例企业",
            "contact_person": "张三",
            "phone": "13800138000",
            "email": "demo@example.com",
            "address": "北京市朝阳区",
        }
    ]
    
    for tenant in tenants:
        db_tenant = crud["tenant"].get_by_name(
            db, 
            tenant_name=tenant["tenant_name"]
        )
        if not db_tenant:
            crud["tenant"].create(db, obj_in=tenant)

    # 检查默认租户是否存在
    db_tenant = crud["tenant"].get_by_name(
        db, 
        tenant_name="Default Tenant"
    )
    if not db_tenant:
        default_tenant = {
            "tenant_name": "Default Tenant",
            "contact_person": "Admin",
            "email": "admin@admin.com",
            "status": "active"
        }
        db_tenant = crud["tenant"].create(db=db, obj_in=default_tenant)
        logger.info("Default tenant created")


def main() -> None:
    init()
    logger.info("初始数据创建完成")


if __name__ == "__main__":
    main() 