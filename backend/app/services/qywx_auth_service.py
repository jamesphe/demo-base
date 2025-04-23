import httpx
import json
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.tenant import Tenant
from app.models.user import User
from app.models.qywx_auth_events import QywxAuthEvents
from app.models.role import Role
from app.models.user_role import UserRole
from app.services.tenant_service import create_tenant
from app.db.session import redis_client
import logging

logger = logging.getLogger(__name__)

# Suite Ticket 缓存键
SUITE_TICKET_KEY = "qywx:suite_ticket"
# Suite Access Token 缓存键
SUITE_TOKEN_KEY = "qywx:suite_token"
# Provider Token 缓存键
PROVIDER_TOKEN_KEY = "qywx:provider_token"
# 企业 Token 缓存键前缀
CORP_TOKEN_PREFIX = "qywx:corp_token:"


async def save_suite_ticket(ticket: str, expires: int = 1200):
    """保存 suite_ticket 到 Redis
    
    Args:
        ticket: suite_ticket
        expires: 过期时间，单位秒，默认20分钟
    """
    try:
        redis_client.set(SUITE_TICKET_KEY, ticket, ex=expires)
        logger.info(f"保存suite_ticket成功: {ticket}")
        return True
    except Exception as e:
        logger.exception(f"保存suite_ticket失败: {e}")
        return False


def get_suite_ticket():
    """从 Redis 获取 suite_ticket"""
    try:
        ticket = redis_client.get(SUITE_TICKET_KEY)
        if ticket:
            return ticket.decode()
        logger.warning("未找到suite_ticket")
        return None
    except Exception as e:
        logger.exception(f"获取suite_ticket失败: {e}")
        return None


async def get_provider_token():
    """获取服务商凭证
    
    返回值:
        provider_access_token: 服务商凭证
    """
    try:
        # 尝试从缓存获取
        token = redis_client.get(PROVIDER_TOKEN_KEY)
        if token:
            return token.decode()
        
        # 调用接口获取
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://qyapi.weixin.qq.com/cgi-bin/service/get_provider_token",
                json={
                    "corpid": settings.QYWX_PROVIDER_CORPID,
                    "provider_secret": settings.QYWX_PROVIDER_SECRET
                }
            )
            data = resp.json()
            
            if data.get("errcode") == 0:
                token = data.get("provider_access_token")
                expires_in = data.get("expires_in", 7200)
                # 保存到 Redis，提前10分钟过期
                redis_client.set(
                    PROVIDER_TOKEN_KEY, 
                    token, 
                    ex=expires_in - 600 if expires_in > 600 else expires_in
                )
                return token
            else:
                logger.error(f"获取provider_token失败: {data}")
                return None
    except Exception as e:
        logger.exception(f"获取provider_token异常: {e}")
        return None


async def get_suite_token():
    """获取第三方应用凭证
    
    返回值:
        suite_access_token: 第三方应用凭证
    """
    try:
        # 尝试从缓存获取
        token = redis_client.get(SUITE_TOKEN_KEY)
        if token:
            return token.decode()
        
        # 获取 suite_ticket
        suite_ticket = get_suite_ticket()
        if not suite_ticket:
            logger.error("获取suite_ticket失败")
            return None
        
        # 调用接口获取
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://qyapi.weixin.qq.com/cgi-bin/service/get_suite_token",
                json={
                    "suite_id": settings.QYWX_SUITE_ID,
                    "suite_secret": settings.QYWX_SUITE_SECRET,
                    "suite_ticket": suite_ticket
                }
            )
            data = resp.json()
            
            if data.get("errcode") == 0:
                token = data.get("suite_access_token")
                expires_in = data.get("expires_in", 7200)
                # 保存到 Redis，提前10分钟过期
                redis_client.set(
                    SUITE_TOKEN_KEY, 
                    token, 
                    ex=expires_in - 600 if expires_in > 600 else expires_in
                )
                return token
            else:
                logger.error(f"获取suite_token失败: {data}")
                return None
    except Exception as e:
        logger.exception(f"获取suite_token异常: {e}")
        return None


async def get_corp_token(corp_id: str, permanent_code: str):
    """获取企业凭证
    
    Args:
        corp_id: 授权企业ID
        permanent_code: 永久授权码
        
    返回值:
        access_token: 企业凭证
    """
    try:
        # 缓存键
        cache_key = f"{CORP_TOKEN_PREFIX}{corp_id}"
        
        # 尝试从缓存获取
        token = redis_client.get(cache_key)
        if token:
            return token.decode()
        
        # 获取 suite_token
        suite_token = await get_suite_token()
        if not suite_token:
            logger.error("获取suite_token失败")
            return None
        
        # 调用接口获取
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"https://qyapi.weixin.qq.com/cgi-bin/service/get_corp_token?suite_access_token={suite_token}",
                json={
                    "auth_corpid": corp_id,
                    "permanent_code": permanent_code
                }
            )
            data = resp.json()
            
            if data.get("errcode") == 0:
                token = data.get("access_token")
                expires_in = data.get("expires_in", 7200)
                # 保存到 Redis，提前10分钟过期
                redis_client.set(
                    cache_key, 
                    token, 
                    ex=expires_in - 600 if expires_in > 600 else expires_in
                )
                return token
            else:
                logger.error(f"获取企业凭证失败: {data}")
                return None
    except Exception as e:
        logger.exception(f"获取企业凭证异常: {e}")
        return None


async def get_permanent_code(auth_code: str, db: Session):
    """使用临时授权码获取永久授权码
    
    Args:
        auth_code: 临时授权码
        db: 数据库会话
        
    返回值:
        auth_info: 授权信息
    """
    try:
        # 获取 suite_token
        suite_token = await get_suite_token()
        if not suite_token:
            logger.error("获取suite_token失败")
            return None
        
        # 调用接口获取永久授权码
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"https://qyapi.weixin.qq.com/cgi-bin/service/get_permanent_code?suite_access_token={suite_token}",
                json={"auth_code": auth_code}
            )
            data = resp.json()
            
            if data.get("errcode") == 0:
                # 返回授权信息
                return data
            else:
                logger.error(f"获取永久授权码失败: {data}")
                return None
    except Exception as e:
        logger.exception(f"获取永久授权码异常: {e}")
        return None


async def handle_create_auth(auth_code: str, db: Session):
    """处理企业授权事件
    
    Args:
        auth_code: 临时授权码
        db: 数据库会话
        
    返回值:
        tenant: 租户对象
    """
    try:
        # 获取永久授权码
        auth_info = await get_permanent_code(auth_code, db)
        if not auth_info:
            logger.error("获取永久授权码失败")
            return None
        
        # 提取企业信息
        corp_id = auth_info.get("auth_corp_info").get("corpid")
        corp_name = auth_info.get("auth_corp_info").get("corp_name")
        permanent_code = auth_info.get("permanent_code")
        agent_id = auth_info.get("auth_info").get("agent").get("agentid")
        auth_user_id = auth_info.get("auth_user_info").get("userid")
        
        # 查找租户
        tenant = db.query(Tenant).filter(Tenant.qywx_corp_id == corp_id).first()
        
        if not tenant:
            # 创建新租户
            tenant = create_tenant(
                db=db,
                tenant_data={
                    "tenant_name": corp_name,
                    "qywx_corp_id": corp_id,
                    "qywx_permanent_code": permanent_code,
                    "qywx_agent_id": agent_id,
                    "auth_user_id": auth_user_id,
                    "auth_time": datetime.now(),
                    "subscription_type": "trial",
                    "subscription_start": datetime.now(),
                    "subscription_end": datetime.now() + timedelta(days=15)  # 15天试用期
                }
            )
        else:
            # 更新现有租户
            tenant.tenant_name = corp_name
            tenant.qywx_permanent_code = permanent_code
            tenant.qywx_agent_id = agent_id
            tenant.auth_user_id = auth_user_id
            tenant.auth_time = datetime.now()
            db.commit()
            db.refresh(tenant)
        
        # 记录授权事件
        auth_event = QywxAuthEvents(
            tenant_id=tenant.tenant_id,
            qywx_corp_id=corp_id,
            event_type="create_auth",
            event_time=datetime.now(),
            event_data=json.dumps(auth_info)
        )
        db.add(auth_event)
        db.commit()
        
        # 同步企业通讯录
        from app.services.qywx_contact_service import sync_corp_contacts
        await sync_corp_contacts(tenant.tenant_id, db)
        
        return tenant
    except Exception as e:
        db.rollback()
        logger.exception(f"处理企业授权事件异常: {e}")
        return None


async def handle_cancel_auth(corp_id: str, db: Session):
    """处理取消授权事件
    
    Args:
        corp_id: 企业ID
        db: 数据库会话
    """
    try:
        # 查找租户
        tenant = db.query(Tenant).filter(Tenant.qywx_corp_id == corp_id).first()
        if not tenant:
            logger.warning(f"未找到企业: {corp_id}")
            return
        
        # 记录取消授权事件
        auth_event = QywxAuthEvents(
            tenant_id=tenant.tenant_id,
            qywx_corp_id=corp_id,
            event_type="cancel_auth",
            event_time=datetime.now()
        )
        db.add(auth_event)
        
        # 更新租户状态
        tenant.status = "inactive"
        tenant.expiry_time = datetime.now()
        db.commit()
        
        # 清除企业凭证缓存
        cache_key = f"{CORP_TOKEN_PREFIX}{corp_id}"
        redis_client.delete(cache_key)
        
        logger.info(f"企业 {corp_id} 取消授权，租户状态已更新")
    except Exception as e:
        db.rollback()
        logger.exception(f"处理取消授权事件异常: {e}")


async def check_auth_status(tenant_id: int, db: Session):
    """检查企业授权状态
    
    Args:
        tenant_id: 租户ID
        db: 数据库会话
        
    返回值:
        is_valid: 授权是否有效
    """
    try:
        # 查找租户
        tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
        if not tenant or not tenant.qywx_corp_id or not tenant.qywx_permanent_code:
            return False
        
        # 获取suite_token
        suite_token = await get_suite_token()
        if not suite_token:
            logger.error("获取suite_token失败")
            return False
        
        # 调用接口获取授权信息
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"https://qyapi.weixin.qq.com/cgi-bin/service/get_auth_info?suite_access_token={suite_token}",
                json={
                    "auth_corpid": tenant.qywx_corp_id,
                    "permanent_code": tenant.qywx_permanent_code
                }
            )
            data = resp.json()
            
            if data.get("errcode") == 0:
                # 授权有效
                return True
            else:
                # 授权无效
                logger.warning(f"租户 {tenant_id} 授权无效: {data}")
                return False
    except Exception as e:
        logger.exception(f"检查授权状态异常: {e}")
        return False 