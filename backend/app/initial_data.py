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
                "job_create"
            ]
        },
        {
            "name": "interviewer",
            "description": "面试官",
            "permissions": [
                "candidate_read",
                "interview_read",
                "interview_create"
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
            name=tenant["tenant_name"]
        )
        if not db_tenant:
            tenant_in = TenantCreate(**tenant)
            crud["tenant"].create(db, obj_in=tenant_in)

    # 检查默认租户是否存在
    db_tenant = crud["tenant"].get_by_name(
        db, 
        name="Default Tenant"
    )
    if not db_tenant:
        tenant_in = TenantCreate(
            tenant_name="Default Tenant",
            contact_person="Admin",
            email="admin@admin.com",
            status="active"
        )
        db_tenant = crud["tenant"].create(db=db, obj_in=tenant_in)
        logger.info("Default tenant created")


def main() -> None:
    init()
    logger.info("初始数据创建完成")


if __name__ == "__main__":
    main() 