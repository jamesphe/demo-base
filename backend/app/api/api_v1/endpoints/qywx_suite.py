from fastapi import APIRouter, Request, Depends, HTTPException, BackgroundTasks
from app.core.config import settings
from app.utils.qywx_crypt import WXBizMsgCrypt
from app.services.qywx_auth_service import (
    save_suite_ticket, 
    handle_create_auth, 
    handle_cancel_auth
)
from app.db.session import get_db
from sqlalchemy.orm import Session
import xml.etree.ElementTree as ET
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/suite/receive")
async def verify_receive_url(msg_signature: str, timestamp: str, nonce: str, echostr: str):
    """验证第三方应用回调URL
    
    用于企业微信验证回调URL有效性
    """
    try:
        wxcpt = WXBizMsgCrypt(
            settings.QYWX_TOKEN, 
            settings.QYWX_ENCODING_AES_KEY, 
            settings.QYWX_SUITE_ID
        )
        ret, sEchoStr = wxcpt.VerifyURL(msg_signature, timestamp, nonce, echostr)
        
        if ret == 0:
            return sEchoStr
        else:
            logger.error(f"验证URL失败，错误码: {ret}")
            raise HTTPException(status_code=400, detail=f"验证失败，错误码: {ret}")
    except Exception as e:
        logger.exception(f"验证URL异常: {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误")


@router.post("/suite/receive")
async def receive_suite_event(
    request: Request, 
    msg_signature: str, 
    timestamp: str, 
    nonce: str, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """接收企业微信第三方应用回调事件
    
    用于接收suite_ticket和授权事件等
    """
    try:
        # 读取请求体
        req_data = await request.body()
        
        # 解密消息
        wxcpt = WXBizMsgCrypt(
            settings.QYWX_TOKEN, 
            settings.QYWX_ENCODING_AES_KEY, 
            settings.QYWX_SUITE_ID
        )
        ret, msg = wxcpt.DecryptMsg(req_data, msg_signature, timestamp, nonce)
        
        if ret != 0:
            logger.error(f"消息解密失败，错误码: {ret}")
            raise HTTPException(status_code=400, detail=f"消息解密失败，错误码: {ret}")
        
        # 解析XML消息
        xml_tree = ET.fromstring(msg)
        info_type = xml_tree.find("InfoType").text
        
        # 根据不同类型处理事件
        if info_type == "suite_ticket":
            # 处理suite_ticket，用于获取suite_access_token
            suite_ticket = xml_tree.find("SuiteTicket").text
            background_tasks.add_task(save_suite_ticket, suite_ticket)
            logger.info(f"接收到suite_ticket: {suite_ticket}")
            
        elif info_type == "create_auth":
            # 企业授权应用事件
            auth_code = xml_tree.find("AuthCode").text
            background_tasks.add_task(handle_create_auth, auth_code, db)
            logger.info(f"接收到create_auth事件，AuthCode: {auth_code}")
            
        elif info_type == "cancel_auth":
            # 取消授权事件
            auth_corp_id = xml_tree.find("AuthCorpId").text
            background_tasks.add_task(handle_cancel_auth, auth_corp_id, db)
            logger.info(f"接收到cancel_auth事件，AuthCorpId: {auth_corp_id}")
            
        elif info_type == "change_auth":
            # 授权变更事件
            auth_corp_id = xml_tree.find("AuthCorpId").text
            logger.info(f"接收到change_auth事件，AuthCorpId: {auth_corp_id}")
            
        elif info_type == "reset_permanent_code":
            # 重置永久授权码事件
            auth_code = xml_tree.find("AuthCode").text
            background_tasks.add_task(handle_create_auth, auth_code, db)
            logger.info(f"接收到reset_permanent_code事件，AuthCode: {auth_code}")
            
        else:
            logger.warning(f"未知的InfoType: {info_type}")
        
        # 返回成功
        return "success"
    except Exception as e:
        logger.exception(f"处理回调事件异常: {e}")
        # 即使出错也返回成功，避免企业微信重复推送
        return "success" 