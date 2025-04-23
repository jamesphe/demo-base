from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from app.core.config import settings
from app.db.session import get_db
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.tenant import Tenant
from app.core.security import create_access_token
from app.services.qywx_auth_service import get_corp_token
import httpx
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/qywx/web-auth")
async def qywx_web_auth(redirect_uri: str):
    """生成企业微信网页授权链接
    
    Args:
        redirect_uri: 授权后重定向的地址
    """
    auth_url = (
        f"https://open.work.weixin.qq.com/wwopen/sso/qrConnect"
        f"?appid={settings.QYWX_SUITE_ID}"
        f"&agentid={settings.QYWX_SUITE_ID}"
        f"&redirect_uri={redirect_uri}"
        f"&state=STATE"
    )
    return {"auth_url": auth_url}


@router.get("/qywx/login-url")
async def get_qywx_login_url():
    """获取企业微信登录URL
    
    返回用于前端登录页面的企业微信扫码登录URL
    """
    try:
        # 构建重定向URL（前端登录回调页面）
        base_url = settings.FRONTEND_BASE_URL
        redirect_uri = f"{base_url}/login?authType=qywx"
        
        # 构建企业微信扫码登录URL
        auth_url = (
            f"https://open.work.weixin.qq.com/wwopen/sso/qrConnect"
            f"?appid={settings.QYWX_SUITE_ID}"
            f"&agentid={settings.QYWX_SUITE_AGENT_ID}"
            f"&redirect_uri={redirect_uri}"
            f"&state=STATE"
        )
        
        return {"auth_url": auth_url}
    except Exception as e:
        logger.exception(f"获取企业微信登录URL异常: {e}")
        raise HTTPException(status_code=500, detail="获取企业微信登录URL失败")


@router.post("/qywx/login")
async def qywx_login(code: str, appid: str, db: Session = Depends(get_db)):
    """企业微信网页授权登录
    
    Args:
        code: 企业微信授权code
        appid: 企业微信CorpID
    """
    try:
        # 查找租户
        tenant = db.query(Tenant).filter(Tenant.qywx_corp_id == appid).first()
        if not tenant:
            raise HTTPException(status_code=401, detail="未授权的企业")
        
        # 获取企业访问令牌
        corp_token = await get_corp_token(tenant.qywx_corp_id, tenant.qywx_permanent_code)
        if not corp_token:
            raise HTTPException(status_code=500, detail="获取企业访问令牌失败")
        
        # 获取用户身份
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"https://qyapi.weixin.qq.com/cgi-bin/user/getuserinfo?access_token={corp_token}&code={code}"
            )
            user_data = resp.json()
            
            if user_data.get("errcode") != 0:
                logger.error(f"获取用户信息失败: {user_data}")
                raise HTTPException(status_code=401, detail="获取用户信息失败")
            
            userid = user_data.get("userid")
            if not userid:
                raise HTTPException(status_code=401, detail="未获取到用户ID")
            
            # 查找用户
            user = db.query(User).filter(
                User.tenant_id == tenant.tenant_id,
                User.qywx_userid == userid
            ).first()
            
            if not user:
                # 获取详细用户信息
                user_detail_resp = await client.get(
                    f"https://qyapi.weixin.qq.com/cgi-bin/user/get?access_token={corp_token}&userid={userid}"
                )
                user_detail = user_detail_resp.json()
                
                if user_detail.get("errcode") != 0:
                    logger.error(f"获取用户详情失败: {user_detail}")
                    raise HTTPException(status_code=401, detail="获取用户详情失败")
                
                # 创建新用户
                user = User(
                    tenant_id=tenant.tenant_id,
                    username=f"{userid}@{tenant.qywx_corp_id}",
                    password="qywx_auth_user",  # 占位密码，实际使用企微认证
                    email=user_detail.get("email", ""),
                    phone=user_detail.get("mobile", ""),
                    user_type="tenant",
                    qywx_userid=userid,
                    qywx_avatar=user_detail.get("avatar", "")
                )
                db.add(user)
                db.commit()
                db.refresh(user)
        
        # 创建访问令牌
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        token = create_access_token(
            data={"sub": user.username, "tenant_id": tenant.tenant_id},
            expires_delta=access_token_expires
        )
        
        return {
            "token": token,
            "token_type": "bearer",
            "user": {
                "username": user.username,
                "email": user.email,
                "tenant_id": tenant.tenant_id,
                "tenant_name": tenant.tenant_name
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"企业微信登录异常: {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误")


@router.get("/qywx/jsapi_config")
async def get_jsapi_config(url: str, db: Session = Depends(get_db)):
    """获取企业微信JS-SDK配置
    
    Args:
        url: 当前网页的URL，不包含#及其后面部分
    """
    try:
        from app.api.deps import get_current_tenant_id
        tenant_id = await get_current_tenant_id(db)
        
        # 获取租户信息
        tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
        if not tenant:
            raise HTTPException(status_code=401, detail="未授权的租户")
        
        # 获取企业访问令牌
        corp_token = await get_corp_token(tenant.qywx_corp_id, tenant.qywx_permanent_code)
        if not corp_token:
            raise HTTPException(status_code=500, detail="获取企业访问令牌失败")
        
        # 获取jsapi_ticket
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"https://qyapi.weixin.qq.com/cgi-bin/get_jsapi_ticket?access_token={corp_token}"
            )
            ticket_data = resp.json()
            
            if ticket_data.get("errcode") != 0:
                logger.error(f"获取jsapi_ticket失败: {ticket_data}")
                raise HTTPException(status_code=500, detail="获取jsapi_ticket失败")
            
            jsapi_ticket = ticket_data.get("ticket")
            
            # 计算签名
            import time
            import hashlib
            import random
            import string
            
            noncestr = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(16))
            timestamp = int(time.time())
            
            # 按字典序排序
            sign_list = [
                f"jsapi_ticket={jsapi_ticket}",
                f"noncestr={noncestr}",
                f"timestamp={timestamp}",
                f"url={url}"
            ]
            sign_str = "&".join(sorted(sign_list))
            
            # 计算签名
            signature = hashlib.sha1(sign_str.encode()).hexdigest()
            
            return {
                "errcode": 0,
                "config": {
                    "corpid": tenant.qywx_corp_id,
                    "agentid": tenant.qywx_agent_id,
                    "noncestr": noncestr,
                    "timestamp": timestamp,
                    "signature": signature
                }
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"获取JS-SDK配置异常: {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误") 