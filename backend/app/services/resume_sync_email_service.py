import logging
import sys
import os
import ssl
import socket
import imaplib
import email
import smtplib
from datetime import datetime
from email.header import decode_header
from typing import List, Optional, Any, Dict
from fastapi import HTTPException
from sqlalchemy.orm import Session
from imap_tools import MailBox, A, MailMessageFlags

from app import models, schemas
from app.core.celery_config import celery_app
from app.services.resume_service import resume_service
from app.db.session import SessionLocal
from app.services.resume_queue_service import process_resume_task


# 重新配置日志
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # 设置为DEBUG级别，输出所有日志

# 如果没有处理器，添加一个新的处理器
if not logger.handlers:
    # 创建控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    
    # 设置详细的日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - '
        '%(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

# 设置IMAP库的调试级别
imaplib.Debug = 4  # 设置IMAP库的调试级别为最高

class ResumeSyncEmailService:
    """简历邮件同步服务"""
    
    def __init__(self):
        self.db = SessionLocal()
    
    def get_active_sync_emails(self) -> List[models.ResumeSyncEmail]:
        """获取所有活跃的同步邮箱配置"""
        # 先获取所有记录，看看数据库中实际的值是什么
        all_emails = self.db.query(models.ResumeSyncEmail).all()
        email_info = [(e.email, e.is_active) for e in all_emails]
        logger.info(f"数据库中所有记录: {email_info}")
        
        # 使用更直接的比较方式
        query = self.db.query(models.ResumeSyncEmail).filter(
            models.ResumeSyncEmail.is_active == True  # noqa: E712
        )
        results = query.all()
        logger.info(f"活跃邮箱查询结果: {[email.email for email in results]}")
        return results
    
    def update_sync_time(self, email_id: int) -> None:
        """更新邮箱最后同步时间"""
        sync_email = self.db.query(models.ResumeSyncEmail).filter(
            models.ResumeSyncEmail.id == email_id
        ).first()
        if sync_email:
            sync_email.last_sync_time = datetime.utcnow()
            self.db.commit()
    
    def get_job_keywords(self, sync_email_id: int) -> List[models.JobKeyword]:
        """获取邮箱关联的职位关键字"""
        return self.db.query(models.JobKeyword).filter(
            models.JobKeyword.sync_email_id == sync_email_id
        ).all()
    
    def get_tenant_admin(self, tenant_id: int) -> Optional[models.User]:
        """获取租户的管理员用户"""
        # 首先查询tenant_admin角色
        tenant_admin_role = self.db.query(models.Role).filter(
            models.Role.name == "tenant_admin"
        ).first()
        
        if not tenant_admin_role:
            return None
            
        # 查询同时具有该角色且属于指定租户的用户
        user = self.db.query(models.User).filter(
            models.User.tenant_id == tenant_id,
            models.User.roles.any(id=tenant_admin_role.id)
        ).first()
        
        return user
    
    def match_job_by_keyword(
        self,
        subject: str,
        content: str,
        keywords: List[models.JobKeyword]
    ) -> Optional[int]:
        """根据关键字匹配职位"""
        text = f"{subject} {content}".lower()
        for keyword in keywords:
            if keyword.keyword.lower() in text:
                return keyword.job_id
        return None
    
    def save_attachment(
        self,
        tenant_id: int,
        filename: str,
        content: bytes
    ) -> Optional[str]:
        """保存邮件附件"""
        try:
            if not filename:
                return None
                
            # 检查文件类型
            if not resume_service.validate_file_extension(filename):
                return None
                
            # 创建保存目录
            save_dir = os.path.join(
                "uploads",
                "email_attachments",
                str(tenant_id)
            )
            os.makedirs(save_dir, exist_ok=True)
            
            # 生成唯一文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_filename = f"{timestamp}_{filename}"
            filepath = os.path.join(save_dir, unique_filename)
            
            # 保存文件
            with open(filepath, "wb") as f:
                f.write(content)
                
            return filepath
        except Exception as e:
            logger.error(f"保存附件失败: {str(e)}")
            return None
    
    def process_email(
        self,
        sync_email: models.ResumeSyncEmail,
        msg: email.message.Message
    ) -> None:
        """处理单封邮件"""
        try:
            # 记录处理开始
            logger.info(f"开始处理邮件: {msg['message-id']}")
            
            # 获取邮件主题和内容
            subject = decode_header(msg["subject"])[0][0]
            if isinstance(subject, bytes):
                subject = subject.decode()
                
            logger.info(f"邮件主题: {subject}")
            logger.info(f"发件人: {msg['from']}")
            logger.info(f"接收时间: {msg['date']}")
                
            content = ""
            if msg.is_multipart():
                logger.info("处理多部分邮件")
                for part in msg.walk():
                    content_type = part.get_content_type()
                    logger.info(f"处理邮件部分: {content_type}")
                    if content_type == "text/plain":
                        try:
                            content = part.get_payload(decode=True).decode()
                            logger.info(f"已提取文本内容，长度: {len(content)}")
                            break
                        except Exception as e:
                            logger.error(f"解码邮件内容失败: {str(e)}")
            else:
                logger.info("处理单部分邮件")
                try:
                    content = msg.get_payload(decode=True).decode()
                    logger.info(f"已提取文本内容，长度: {len(content)}")
                except Exception as e:
                    logger.error(f"解码邮件内容失败: {str(e)}")
            
            # 获取职位关键字
            keywords = self.get_job_keywords(sync_email.id)
            logger.info(f"找到 {len(keywords)} 个关键字配置")
            
            # 匹配职位
            job_id = self.match_job_by_keyword(subject, content, keywords)
            logger.info(f"关键字匹配结果 - 职位ID: {job_id or '未匹配'}")
            
            # 处理附件
            logger.info("开始处理邮件附件...")
            attachment_count = 0
            processed_count = 0
            
            for part in msg.walk():
                if part.get_content_maintype() == "multipart":
                    logger.info("跳过多部分内容")
                    continue
                    
                if part.get("Content-Disposition") is None:
                    logger.info("跳过无内容处置的部分")
                    continue
                
                filename = part.get_filename()
                if not filename:
                    logger.info("跳过无文件名的附件")
                    continue
                    
                attachment_count += 1
                logger.info(f"处理附件 {attachment_count}: {filename}")
                
                content_type = part.get_content_type()
                logger.info(f"附件类型: {content_type}")
                    
                filepath = self.save_attachment(
                    sync_email.tenant_id,
                    filename,
                    part.get_payload(decode=True)
                )
                
                if not filepath:
                    logger.warning(f"附件 {filename} 保存失败或文件类型不支持")
                    continue
                    
                logger.info(f"附件已保存到: {filepath}")
                processed_count += 1
                    
                # 创建简历记录
                # 尝试获取租户管理员用户
                admin_user = self.get_tenant_admin(
                    sync_email.tenant_id
                )
                
                # 如果找不到管理员用户，则创建模拟系统用户
                if not admin_user:
                    admin_user = type('User', (), {
                        'id': 0,
                        'tenant_id': sync_email.tenant_id,
                        'username': 'system',
                        'user_type': 'admin',
                        'is_superuser': False
                    })
                
                resume = resume_service.create_initial_resume(
                    self.db,
                    {
                        "file_name": os.path.basename(filepath),
                        "file_path": filepath,
                        "file_type": os.path.splitext(filepath)[1][1:]
                    },
                    None,  # repository_id
                    admin_user,  # 使用租户管理员或模拟系统用户
                    job_id
                )
                
                logger.info(f"已创建简历记录，ID: {resume.id}")
                
                # 将简历加入处理队列
                process_resume_task.delay(
                    resume.id,
                    **{
                        'publisher_id': None,  # 系统自动处理
                        'job_id': job_id
                    }
                )
                
                logger.info(f"简历 {resume.id} 已加入处理队列")
                
            logger.info(f"附件处理完成: 共 {attachment_count} 个，成功处理 {processed_count} 个")    
                
        except Exception as e:
            logger.error(f"处理邮件失败: {str(e)}")
    
    async def sync_emails(self, sync_email: models.ResumeSyncEmail) -> None:
        """使用imap-tools同步邮箱中的简历"""
        try:
            logger.info(
                f"正在连接到邮箱服务器: "
                f"{sync_email.imap_server}:{sync_email.imap_port}"
            )
            
            # 使用MailBox连接邮箱
            with MailBox(sync_email.imap_server, sync_email.imap_port).login(
                sync_email.email, sync_email.password, initial_folder='INBOX'
            ) as mailbox:
                logger.info(f"邮箱 {sync_email.email} 连接成功")
                
                # 列出所有可用文件夹
                folders = mailbox.folder.list()
                logger.info("可用邮箱文件夹列表:")
                for i, folder in enumerate(folders):
                    logger.info(f"  {i+1}. {folder.name} ({folder.flags})")
                
                # 获取所有未读邮件
                logger.info("搜索未读邮件...")
                messages = mailbox.fetch(A(seen=False))
                
                # 计数器初始化
                processed_count = 0
                success_count = 0
                
                # 处理每封邮件
                for msg in messages:
                    try:
                        processed_count += 1
                        logger.info(
                            f"处理第 {processed_count} 封邮件: {msg.subject}"
                        )
                        
                        # 获取邮件主题和内容
                        subject = msg.subject or ''
                        body = msg.text or ''
                        
                        logger.info(
                            f"邮件详情 - 发件人: {msg.from_}, "
                            f"收件人: {msg.to}, 日期: {msg.date}"
                        )
                        logger.info(f"邮件主题: {subject}")
                        logger.info(f"邮件内容摘要: {body[:100]}...")
                        
                        # 获取职位关键字并进行匹配
                        keywords = self.get_job_keywords(sync_email.id)
                        logger.info(f"找到 {len(keywords)} 个关键字配置")
                        for kw in keywords:
                            logger.info(
                                f"关键字: {kw.keyword}, "
                                f"职位ID: {kw.job_id}"
                            )
                        
                        job_id = self.match_job_by_keyword(subject, body, keywords)
                        logger.info(
                            f"关键字匹配结果 - "
                            f"职位ID: {job_id if job_id else '未匹配'}"
                        )
                        
                        # 处理附件
                        logger.info(f"附件数量: {len(msg.attachments)}")
                        attachments_processed = False
                        for att in msg.attachments:
                            try:
                                if not att.filename:
                                    logger.info("附件没有文件名，跳过")
                                    continue
                                
                                logger.info(
                                    f"处理附件: {att.filename}, "
                                    f"类型: {att.content_type}"
                                )
                                filepath = self.save_attachment(
                                    sync_email.tenant_id,
                                    att.filename,
                                    att.payload
                                )
                                
                                if not filepath:
                                    logger.warning(
                                        f"附件 {att.filename} 保存失败或文件类型不支持"
                                    )
                                    continue
                                
                                logger.info(f"附件已保存到: {filepath}")
                                
                                # 创建简历记录的文件信息
                                file_info = {
                                    "file_name": os.path.basename(filepath),
                                    "file_path": filepath,
                                    "file_type": os.path.splitext(filepath)[1][1:]
                                }
                                
                                # 创建简历记录
                                # 尝试获取租户管理员用户
                                admin_user = self.get_tenant_admin(
                                    sync_email.tenant_id
                                )
                                
                                # 如果找不到管理员用户，则创建模拟系统用户
                                if not admin_user:
                                    admin_user = type('User', (), {
                                        'id': 0,
                                        'tenant_id': sync_email.tenant_id,
                                        'username': 'system',
                                        'user_type': 'admin',
                                        'is_superuser': False
                                    })
                                
                                resume = await resume_service.create_initial_resume(
                                    self.db,
                                    file_info,
                                    None,  # repository_id
                                    admin_user,  # 使用租户管理员或模拟系统用户
                                    job_id
                                )
                                
                                logger.info(f"已创建简历记录，ID: {resume.id}")
                                
                                # 将简历加入处理队列
                                process_resume_task.delay(
                                    resume.id,
                                    **{ 
                                        'publisher_id': admin_user.id,
                                        'job_id': job_id
                                    }
                                )
                                
                                logger.info(f"简历 {resume.id} 已加入处理队列")
                                logger.info(f"附件 {att.filename} 处理成功")
                                attachments_processed = True
                                
                            except Exception as e:
                                logger.error(
                                    f"处理附件 {att.filename} 失败: {str(e)}"
                                )
                        
                        # 标记邮件为已读
                        mailbox.flag(msg.uid, MailMessageFlags.SEEN, True)
                        logger.info("邮件已标记为已读")
                        
                        if attachments_processed:
                            success_count += 1
                            logger.info(f"邮件处理成功，计数器更新: {success_count}")
                        else:
                            logger.info("邮件中没有处理成功的附件")
                            
                    except Exception as e:
                        logger.error(f"处理邮件失败: {str(e)}")
                
                logger.info(
                    f"邮件处理完成: 共 {processed_count} 封，"
                    f"成功处理 {success_count} 封"
                )
            
            # 更新同步时间
            self.update_sync_time(sync_email.id)
            logger.info(f"邮箱 {sync_email.email} 同步时间已更新")
            logger.info("邮箱同步完成")
            
        except Exception as e:
            logger.error(f"同步邮箱失败: {str(e)}")
    
    # 新增的业务逻辑方法

    def create_sync_email(
        self, 
        db: Session,
        sync_email_in: schemas.ResumeSyncEmailCreate,
        tenant_id: int
    ) -> models.ResumeSyncEmail:
        """创建简历同步邮箱配置"""
        # 检查邮箱是否已存在
        existing = db.query(models.ResumeSyncEmail).filter(
            models.ResumeSyncEmail.email == sync_email_in.email,
            models.ResumeSyncEmail.tenant_id == tenant_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=400,
                detail="该邮箱已配置"
            )
        
        # 创建配置
        sync_email = models.ResumeSyncEmail(
            **sync_email_in.dict(),
            tenant_id=tenant_id
        )
        db.add(sync_email)
        db.commit()
        db.refresh(sync_email)
        return sync_email
    
    def get_sync_emails(
        self,
        db: Session,
        page: int = 1,
        per_page: int = 10,
        tenant_id: int = None,
        is_superuser: bool = False
    ) -> Dict[str, Any]:
        """获取简历同步邮箱配置列表（带分页）"""
        skip = (page - 1) * per_page
        
        # 构建查询对象
        query = db.query(models.ResumeSyncEmail)
        
        # 租户过滤
        if not is_superuser and tenant_id is not None:
            query = query.filter(models.ResumeSyncEmail.tenant_id == tenant_id)
        
        # 计算总数
        total = query.count()
        
        # 获取分页数据
        sync_emails = query.offset(skip).limit(per_page).all()
        
        # 计算总页数
        total_pages = (total + per_page - 1) // per_page if total > 0 else 0
        
        return {
            "data": sync_emails,
            "meta": {
                "total": total,
                "page": page,
                "per_page": per_page,
                "total_pages": total_pages
            }
        }
    
    def get_sync_email(
        self,
        db: Session,
        sync_email_id: int,
        tenant_id: int = None,
        is_superuser: bool = False
    ) -> models.ResumeSyncEmail:
        """获取单个简历同步邮箱配置"""
        sync_email = db.query(models.ResumeSyncEmail).filter(
            models.ResumeSyncEmail.id == sync_email_id
        ).first()
        if not sync_email:
            raise HTTPException(status_code=404, detail="配置不存在")
        if not is_superuser and sync_email.tenant_id != tenant_id:
            raise HTTPException(status_code=403, detail="无权访问该配置")
        return sync_email
    
    def update_sync_email(
        self,
        db: Session,
        sync_email_id: int,
        sync_email_in: schemas.ResumeSyncEmailUpdate,
        tenant_id: int = None,
        is_superuser: bool = False
    ) -> models.ResumeSyncEmail:
        """更新简历同步邮箱配置"""
        sync_email = db.query(models.ResumeSyncEmail).filter(
            models.ResumeSyncEmail.id == sync_email_id
        ).first()
        if not sync_email:
            raise HTTPException(status_code=404, detail="配置不存在")
        if not is_superuser and sync_email.tenant_id != tenant_id:
            raise HTTPException(status_code=403, detail="无权访问该配置")
        
        # 检查邮箱是否已被其他配置使用
        if sync_email_in.email and sync_email_in.email != sync_email.email:
            existing = db.query(models.ResumeSyncEmail).filter(
                models.ResumeSyncEmail.email == sync_email_in.email,
                models.ResumeSyncEmail.tenant_id == tenant_id,
                models.ResumeSyncEmail.id != sync_email_id
            ).first()
            if existing:
                raise HTTPException(
                    status_code=400,
                    detail="该邮箱已被其他配置使用"
                )
        
        # 更新配置
        for field, value in sync_email_in.dict(exclude_unset=True).items():
            setattr(sync_email, field, value)
        
        db.commit()
        db.refresh(sync_email)
        return sync_email
    
    def delete_sync_email(
        self,
        db: Session,
        sync_email_id: int,
        tenant_id: int = None,
        is_superuser: bool = False
    ) -> Dict[str, str]:
        """删除简历同步邮箱配置"""
        sync_email = db.query(models.ResumeSyncEmail).filter(
            models.ResumeSyncEmail.id == sync_email_id
        ).first()
        if not sync_email:
            raise HTTPException(status_code=404, detail="配置不存在")
        if not is_superuser and sync_email.tenant_id != tenant_id:
            raise HTTPException(status_code=403, detail="无权访问该配置")
        
        db.delete(sync_email)
        db.commit()
        return {"message": "配置已删除"}
    
    def create_keyword(
        self,
        db: Session,
        sync_email_id: int,
        keyword_in: schemas.JobKeywordCreate,
        tenant_id: int = None,
        is_superuser: bool = False
    ) -> models.JobKeyword:
        """创建职位关键字"""
        # 检查配置是否存在
        sync_email = db.query(models.ResumeSyncEmail).filter(
            models.ResumeSyncEmail.id == sync_email_id
        ).first()
        if not sync_email:
            raise HTTPException(status_code=404, detail="配置不存在")
        if not is_superuser and sync_email.tenant_id != tenant_id:
            raise HTTPException(status_code=403, detail="无权访问该配置")
        
        # 检查邮箱是否已经同步过
        if not sync_email.last_sync_time:
            logger = logging.getLogger(__name__)
            logger.warning(f"邮箱 {sync_email.email} 尚未同步过，无法添加关键字")
            raise HTTPException(
                status_code=400, 
                detail="该邮箱尚未同步过，请先在系统设置中进行测试"
            )
        
        # 检查职位是否存在
        job = db.query(models.Job).filter(
            models.Job.id == keyword_in.job_id
        ).first()
        if not job:
            raise HTTPException(status_code=404, detail="职位不存在")
        if not is_superuser and job.tenant_id != tenant_id:
            raise HTTPException(status_code=403, detail="无权访问该职位")
        
        # 创建关键字
        keyword = models.JobKeyword(
            **keyword_in.dict()
        )
        db.add(keyword)
        db.commit()
        db.refresh(keyword)
        return keyword
    
    def get_keywords(
        self,
        db: Session,
        sync_email_id: int,
        tenant_id: int = None,
        is_superuser: bool = False
    ) -> List[models.JobKeyword]:
        """获取职位关键字列表"""
        # 检查配置是否存在
        sync_email = db.query(models.ResumeSyncEmail).filter(
            models.ResumeSyncEmail.id == sync_email_id
        ).first()
        if not sync_email:
            raise HTTPException(status_code=404, detail="配置不存在")
        if not is_superuser and sync_email.tenant_id != tenant_id:
            raise HTTPException(status_code=403, detail="无权访问该配置")
        
        keywords = db.query(models.JobKeyword).filter(
            models.JobKeyword.sync_email_id == sync_email_id
        ).all()
        return keywords
    
    def update_keyword(
        self,
        db: Session,
        keyword_id: int,
        keyword_in: schemas.JobKeywordUpdate,
        tenant_id: int = None,
        is_superuser: bool = False
    ) -> models.JobKeyword:
        """更新职位关键字"""
        keyword = db.query(models.JobKeyword).filter(
            models.JobKeyword.id == keyword_id
        ).first()
        if not keyword:
            raise HTTPException(status_code=404, detail="关键字不存在")
        
        # 检查配置权限
        sync_email = db.query(models.ResumeSyncEmail).filter(
            models.ResumeSyncEmail.id == keyword.sync_email_id
        ).first()
        if not is_superuser and sync_email.tenant_id != tenant_id:
            raise HTTPException(status_code=403, detail="无权访问该配置")
        
        # 更新关键字
        for field, value in keyword_in.dict(exclude_unset=True).items():
            setattr(keyword, field, value)
        
        db.commit()
        db.refresh(keyword)
        return keyword
    
    def delete_keyword(
        self,
        db: Session,
        keyword_id: int,
        tenant_id: int = None,
        is_superuser: bool = False
    ) -> Dict[str, str]:
        """删除职位关键字"""
        keyword = db.query(models.JobKeyword).filter(
            models.JobKeyword.id == keyword_id
        ).first()
        if not keyword:
            raise HTTPException(status_code=404, detail="关键字不存在")
        
        # 检查配置权限
        sync_email = db.query(models.ResumeSyncEmail).filter(
            models.ResumeSyncEmail.id == keyword.sync_email_id
        ).first()
        if not is_superuser and sync_email.tenant_id != tenant_id:
            raise HTTPException(status_code=403, detail="无权访问该配置")
        
        db.delete(keyword)
        db.commit()
        return {"message": "关键字已删除"}
    
    async def test_email_connection(
        self,
        test_data: schemas.ResumeSyncEmailUpdate
    ) -> Dict[str, Any]:
        """测试邮箱连接"""
        logger.info("开始测试邮箱连接")
        imap_success = False
        smtp_success = False
        error_msg = ""
        
        try:
            # 测试网络连通性
            try:
                logger.info(
                    f"测试IMAP服务器网络连通性: "
                    f"{test_data.imap_server}:{test_data.imap_port}"
                )
                socket.create_connection(
                    (test_data.imap_server, test_data.imap_port), 
                    timeout=10
                )
                logger.info("IMAP服务器网络连通")
            except Exception as e:
                error_msg = f"无法连接到IMAP服务器: {str(e)}"
                logger.error(f"IMAP服务器网络连接失败: {str(e)}")
                return {"success": False, "message": error_msg}
            
            try:
                # 测试IMAP连接
                logger.info(
                    f"尝试连接IMAP服务器: "
                    f"{test_data.imap_server}:{test_data.imap_port}"
                )
                imap = imaplib.IMAP4_SSL(
                    test_data.imap_server, 
                    test_data.imap_port
                )
                logger.info("IMAP连接成功，尝试登录")
                imap.login(test_data.email, test_data.password)
                logger.info("IMAP登录成功")
                imap.logout()
                logger.info("IMAP连接测试完成")
                imap_success = True
            except imaplib.IMAP4.error as e:
                login_err_msg = str(e).lower()
                login_failed = (
                    'failed' in login_err_msg or 'error' in login_err_msg
                )
                
                if 'LOGIN' in str(e) and login_failed:
                    error_msg = (
                        "登录失败：请确认邮箱地址正确，并使用邮箱授权码（而非账户密码）。"
                        "大多数邮箱服务商要求使用专用授权码进行第三方登录。"
                    )
                    logger.error(f"IMAP登录失败，可能需要授权码: {str(e)}")
                else:
                    error_msg = f"IMAP连接失败: {str(e)}"
                    logger.error(f"IMAP连接失败: {str(e)}")
                return {"success": False, "message": error_msg}
            except Exception as e:
                error_msg = f"IMAP连接失败: {str(e)}"
                logger.error(f"IMAP连接或登录失败: {str(e)}")
                return {"success": False, "message": error_msg}
            
            # 测试SMTP网络连通性
            try:
                logger.info(
                    f"测试SMTP服务器网络连通性: "
                    f"{test_data.smtp_server}:{test_data.smtp_port}"
                )
                socket.create_connection(
                    (test_data.smtp_server, test_data.smtp_port), 
                    timeout=10
                )
                logger.info("SMTP服务器网络连通")
            except Exception as e:
                error_msg = f"无法连接到SMTP服务器: {str(e)}"
                logger.error(f"SMTP服务器网络连接失败: {str(e)}")
                return {"success": False, "message": error_msg}
            
            if imap_success:
                try:
                    # 测试SMTP连接
                    logger.info(
                        f"尝试连接SMTP服务器: "
                        f"{test_data.smtp_server}:{test_data.smtp_port}"
                    )
                    context = ssl.create_default_context()
                    with smtplib.SMTP_SSL(
                        test_data.smtp_server, 
                        test_data.smtp_port, 
                        context=context,
                        timeout=10
                    ) as server:
                        logger.info("SMTP连接成功，尝试登录")
                        server.login(test_data.email, test_data.password)
                        logger.info("SMTP登录成功")
                    smtp_success = True
                    logger.info("SMTP连接测试完成")
                except Exception as e:
                    error_msg = f"SMTP连接失败: {str(e)}"
                    logger.error(f"SMTP连接或登录失败: {str(e)}")
                    return {"success": False, "message": error_msg}
            
            if imap_success and smtp_success:
                logger.info("邮箱连接测试全部通过")
                return {"success": True, "message": "连接测试成功"}
            else:
                logger.warning(f"邮箱连接测试未全部通过: {error_msg}")
                return {"success": False, "message": error_msg}
        except Exception as e:
            logger.exception(f"测试过程中发生未预期错误: {str(e)}")
            return {"success": False, "message": f"测试过程中发生错误: {str(e)}"}


@celery_app.task(
    name='app.services.resume_sync_email_service.sync_all_emails'
)
def sync_all_emails():
    """同步所有邮箱的Celery任务"""
    logger.info("开始执行 sync_all_emails 任务")
    service = ResumeSyncEmailService()
    try:
        logger.info("正在获取活跃的同步邮箱配置...")
        sync_emails = service.get_active_sync_emails()
        logger.info(f"找到 {len(sync_emails)} 个活跃的同步邮箱配置")
        
        for index, sync_email in enumerate(sync_emails, 1):
            logger.info(
                f"开始处理第 {index}/{len(sync_emails)} 个邮箱: "
                f"{sync_email.email}"
            )
            try:
                # 使用 asyncio.run 来运行异步函数
                import asyncio
                asyncio.run(service.sync_emails(sync_email))
                logger.info(f"邮箱 {sync_email.email} 同步完成")
            except Exception as e:
                logger.error(f"处理邮箱 {sync_email.email} 时发生错误: {str(e)}")
                continue
                
        logger.info("所有邮箱同步任务执行完成")
    except Exception as e:
        logger.error(f"sync_all_emails 任务执行失败: {str(e)}")
    finally:
        service.db.close()
        logger.info("数据库连接已关闭")
