import httpx
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.tenant import Tenant
from app.models.user import User
from app.models.role import Role
from app.models.user_role import UserRole
from app.services.qywx_auth_service import get_corp_token
import logging

logger = logging.getLogger(__name__)


async def sync_corp_contacts(tenant_id: int, db: Session):
    """同步企业通讯录
    
    Args:
        tenant_id: 租户ID
        db: 数据库会话
    
    Returns:
        bool: 是否同步成功
    """
    try:
        # 获取租户信息
        tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
        if not tenant or not tenant.qywx_corp_id or not tenant.qywx_permanent_code:
            logger.error(f"租户 {tenant_id} 未找到或未授权企业微信")
            return False
        
        # 获取企业访问令牌
        corp_token = await get_corp_token(tenant.qywx_corp_id, tenant.qywx_permanent_code)
        if not corp_token:
            logger.error(f"获取企业 {tenant.qywx_corp_id} 的访问令牌失败")
            return False
        
        # 获取部门列表
        departments = await get_department_list(corp_token)
        if not departments:
            logger.error(f"获取企业 {tenant.qywx_corp_id} 的部门列表失败")
            return False
        
        # 查找租户管理员角色
        admin_role = db.query(Role).filter(Role.role_name == "tenant_admin").first()
        if not admin_role:
            logger.error("未找到租户管理员角色")
            return False
        
        # 获取所有部门的用户
        success = True
        for dept in departments:
            users = await get_department_users(corp_token, dept["id"])
            if not users:
                logger.warning(f"获取部门 {dept['name']} 的用户列表失败")
                success = False
                continue
            
            # 同步用户
            for user_info in users:
                try:
                    # 查找现有用户
                    user = db.query(User).filter(
                        User.tenant_id == tenant_id,
                        User.qywx_userid == user_info["userid"]
                    ).first()
                    
                    if not user:
                        # 创建新用户
                        user = User(
                            tenant_id=tenant_id,
                            username=f"{user_info['userid']}@{tenant.qywx_corp_id}",
                            password="qywx_auth_user",  # 占位密码，实际使用企微认证
                            email=user_info.get("email", ""),
                            phone=user_info.get("mobile", ""),
                            user_type="tenant",
                            qywx_userid=user_info["userid"],
                            qywx_avatar=user_info.get("avatar", "")
                        )
                        db.add(user)
                        db.flush()  # 获取用户ID
                        
                        # 如果是授权管理员，分配管理员角色
                        if user_info["userid"] == tenant.auth_user_id:
                            user_role = UserRole(
                                user_id=user.user_id,
                                role_id=admin_role.role_id
                            )
                            db.add(user_role)
                    else:
                        # 更新现有用户
                        user.email = user_info.get("email", user.email)
                        user.phone = user_info.get("mobile", user.phone)
                        user.qywx_avatar = user_info.get("avatar", user.qywx_avatar)
                except Exception as e:
                    logger.exception(f"同步用户 {user_info['userid']} 失败: {e}")
                    success = False
        
        # 提交事务
        db.commit()
        logger.info(f"同步企业 {tenant.qywx_corp_id} 的通讯录完成")
        return success
    except Exception as e:
        db.rollback()
        logger.exception(f"同步企业通讯录异常: {e}")
        return False


async def get_department_list(corp_token: str):
    """获取部门列表
    
    Args:
        corp_token: 企业访问令牌
    
    Returns:
        list: 部门列表
    """
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"https://qyapi.weixin.qq.com/cgi-bin/department/list?access_token={corp_token}"
            )
            data = resp.json()
            
            if data.get("errcode") == 0:
                return data.get("department", [])
            else:
                logger.error(f"获取部门列表失败: {data}")
                return None
    except Exception as e:
        logger.exception(f"获取部门列表异常: {e}")
        return None


async def get_department_users(corp_token: str, department_id: int):
    """获取部门用户列表
    
    Args:
        corp_token: 企业访问令牌
        department_id: 部门ID
    
    Returns:
        list: 用户列表
    """
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"https://qyapi.weixin.qq.com/cgi-bin/user/list?access_token={corp_token}&department_id={department_id}"
            )
            data = resp.json()
            
            if data.get("errcode") == 0:
                return data.get("userlist", [])
            else:
                logger.error(f"获取部门 {department_id} 的用户列表失败: {data}")
                return None
    except Exception as e:
        logger.exception(f"获取部门用户列表异常: {e}")
        return None 