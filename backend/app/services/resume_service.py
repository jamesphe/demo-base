from typing import List, Dict, Any, Optional, Union
from sqlalchemy.orm import Session
from fastapi import (
    UploadFile, HTTPException, BackgroundTasks
)
from datetime import datetime
import uuid
import os
import aiofiles
from sqlalchemy import and_, or_
import shutil
from pydantic import ValidationError
import logging
from pprint import pformat
import json
import time
import random
import subprocess
from pathlib import Path
from sqlalchemy import String
import asyncio
from app import models, crud, schemas
from app.core.config import settings
from app.schemas.resume import (
    ResumeCreate, ResumeUpdate, SkillInfo, CertificateInfo
)
from .base import BaseService
from app.services import (
    repository_service,
    llm_config_service
)
from app.services.job_service import JobService
from app.services.parser_service import parser_service
from app.services.llm_service import llm_service
from app.db.session import SessionLocal

# 创建服务实例
job_service = JobService()

# 设置日志记录器
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# 添加控制台处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# 设置日志格式
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
console_handler.setFormatter(formatter)

# 添加处理器到logger
if not logger.handlers:
    logger.addHandler(console_handler)

class DateTimeEncoder(json.JSONEncoder):
    """处理datetime的JSON编码器"""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

class ResumeService(BaseService[models.Resume, ResumeCreate, ResumeUpdate]):
    """简历服务"""
    
    def __init__(self):
        super().__init__(models.Resume)
        self._setup_logger()
        self.json_encoder = DateTimeEncoder()
        self._setup_conversion_dir()

    def _setup_logger(self) -> None:
        """配置日志"""
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(
            logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        )
        logger.addHandler(console_handler)
        logger.setLevel(logging.DEBUG)

    def _setup_conversion_dir(self):
        """设置文件转换目录"""
        self.conversion_dir = os.path.join(settings.UPLOAD_DIR, 'conversions')
        os.makedirs(self.conversion_dir, exist_ok=True)

    def validate_file_extension(self, filename: str) -> bool:
        """验证文件扩展名是否允许"""
        ext = filename.split(".")[-1].lower()
        return ext in settings.ALLOWED_EXTENSIONS

    async def get_or_create_repository(
        self,
        db: Session,
        *,
        name: str,
        resume_type: str,
        description: Optional[str] = None,
        tenant_id: int
    ) -> models.ResumeRepository:
        """获取或创建简历库"""
        # 先尝试获取已存在的简历库
        repository = repository_service.get_by_name(
            db, 
            name=name,
            tenant_id=tenant_id
        )
        
        # 如果不存在则创建新的
        if not repository:
            repository = await repository_service.create_repository(
                db,
                name=name,
                resume_type=resume_type,
                description=description,
                tenant_id=tenant_id
            )
        
        return repository

    async def process_resume_file(
        self,
        db: Session,
        file: UploadFile,
        repository_id: Optional[int],
        current_user: models.User,
        job_id: Optional[int] = None,
        background_tasks: Optional[BackgroundTasks] = None
    ) -> models.Resume:
        """处理上传的简历文件"""
        file_info = None
        resume = None
        try:
            # 保存文件
            file_info = await self._save_file(
                file, 
                repository_id if repository_id else 'default'
            )
            
            # 创建初始简历记录
            resume = await self.create_initial_resume(
                db=db,
                file_info=file_info,
                repository_id=repository_id,
                current_user=current_user,
                job_id=job_id
            )
            
            # 解析和分析简历
            resume_data = await self._parse_and_analyze_resume(db, file_info)
            logger.info(f"解析和分析简历: {pformat(resume_data)}")
            
            # 准备基础数据
            resume_data.update({
                "repository_id": repository_id,
                "file_path": file_info["file_path"],
                "file_name": file_info["file_name"],
                "file_type": file_info["file_type"],
                "processing_status": "completed",
                "review_status": "pending"
            })
            
            # 使用统一的创建方法
            resume = self.create_resume_with_job(
                db=db,
                resume_data=resume_data,
                current_user=current_user,
                job_id=job_id,
                background_tasks=background_tasks
            )

            return resume
                
        except ValueError as e:
            error_msg = str(e)
            if resume:
                # 更新简历状态为验证失败
                resume = self.update(
                    db=db,
                    db_obj=resume,
                    obj_in=ResumeUpdate(
                        processing_status="validation_failed",
                        processing_error=error_msg
                    )
                )
            return resume
                
        except Exception as e:
            error_msg = f"简历处理失败: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            if resume:
                # 更新简历状态为处理失败
                resume = self.update(
                    db=db,
                    db_obj=resume,
                    obj_in=ResumeUpdate(
                        processing_status="failed",
                        processing_error=error_msg
                    )
                )
            return resume
            
        finally:
            # 如果出错且没有成功创建简历，则清理文件
            if (file_info and file_info.get('file_path') and 
                    not resume):
                self._delete_file(file_info['file_path'])

    async def _save_file(
        self, 
        file: UploadFile, 
        repository_id: Union[int, str]
    ) -> Dict[str, str]:
        """保存上传的文件
        
        Args:
            file: 上传的文件
            repository_id: 简历库ID或默认目录名
        """
        if not self.validate_file_extension(file.filename):
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件类型: {file.filename}"
            )
            
        resume_id = str(uuid.uuid4())
        ext = file.filename.split(".")[-1].lower()
        unique_filename = f"{resume_id}.{ext}"
        
        # 构建存储路径
        repository_path = os.path.join(
            settings.UPLOAD_DIR, 
            str(repository_id)
        )
        os.makedirs(repository_path, exist_ok=True)
        
        file_path = os.path.join(repository_path, unique_filename)
        
        # 保存文件
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)
            
        return {
            "resume_id": resume_id,
            "file_name": file.filename,
            "file_path": file_path,
            "file_type": ext
        }

    def _validate_file_extension(self, filename: str) -> bool:
        """验证文件扩展名"""
        ext = filename.split(".")[-1].lower()
        return ext in settings.ALLOWED_EXTENSIONS

    def _generate_file_info(
        self, 
        file: UploadFile, 
        repository_id: int
    ) -> Dict[str, str]:
        """生成文件信息"""
        resume_id = str(uuid.uuid4())
        ext = file.filename.split(".")[-1].lower()
        unique_filename = f"{resume_id}.{ext}"
        
        repository_path = os.path.join(
            settings.UPLOAD_DIR, 
            str(repository_id)
        )
        os.makedirs(repository_path, exist_ok=True)
        
        return {
            "resume_id": resume_id,
            "file_name": file.filename,
            "file_path": os.path.join(repository_path, unique_filename),
            "file_type": ext
        }

    async def _write_file(self, file: UploadFile, file_path: str) -> None:
        """写入文件"""
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)

    async def _parse_and_analyze_resume(
        self, 
        db: Session,
        file_info: Dict[str, str]
    ) -> Dict[str, Any]:
        """解析和分析简历"""
        # 解析简历文本
        resume_text = await parser_service.parse_resume(file_info["file_path"])
        
        # 获取LLM配置并分析简历
        llm_config = await llm_service.get_default_config(db)
        analysis_result = await self._analyze_resume_with_llm(
            resume_text, 
            llm_config
        )
        
        # 标准化解析结果,确保与Resume模型字段一致
        standardized_data = {
            # 基本信息
            "content": resume_text,
            "parsed_data": analysis_result,
            
            # 个人基本信息
            "name": analysis_result.get("name"),
            "gender": analysis_result.get("gender"),
            "birthdate": analysis_result.get("birthdate"),
            "id_number": analysis_result.get("id_number"),
            "phone": analysis_result.get("phone"),
            "email": analysis_result.get("email"),
            "stature": analysis_result.get("stature"),
            "weight": analysis_result.get("weight"),
            "nation": analysis_result.get("nation"),
            "english_level": analysis_result.get("english_level"),
            "city": analysis_result.get("city"),
            "district": analysis_result.get("district"),
            
            # 个人状态信息
            "political_status": analysis_result.get("political_status"),
            "marital_status": analysis_result.get("marital_status"),
            "hukou": analysis_result.get("hukou"),
            "current_address": analysis_result.get("current_address"),
            
            # 教育信息
            "highest_education": analysis_result.get("highest_education"),
            "highest_degree": analysis_result.get("highest_degree"),
            "major": analysis_result.get("major"),
            "graduate_school": analysis_result.get("graduate_school"),
            "graduation_date": analysis_result.get("graduation_date"),
            
            # 工作经验
            "experience_years": analysis_result.get("experience_years"),
            "current_company": analysis_result.get("current_company"),
            "current_position": analysis_result.get("current_position"),
            "current_salary": analysis_result.get("current_salary"),
            "work_history": analysis_result.get("work_history", []),
            
            # 求职意向
            "expected_position": analysis_result.get("expected_position"),
            "expected_salary": analysis_result.get("expected_salary"),
            "expected_location": analysis_result.get("expected_location"),
            
            # 技能与证书
            "skills": analysis_result.get("skills", []),
            "certificates": analysis_result.get("certificates", []),
            
            # 职称信息
            "talent_name": analysis_result.get("talent_name"),
            "talent_team": analysis_result.get("talent_team"),
            "talent_type": analysis_result.get("talent_type"),
            "title_rank": analysis_result.get("title_rank"),
            
            # 经历信息
            "edu_experience": analysis_result.get("edu_experience", []),
            "awards": analysis_result.get("awards", []),
            
            # 其他信息
            "family_situation": analysis_result.get("family_situation"),
            "other_info": analysis_result.get("other_info"),
            
            # 处理状态
            "processing_status": "pending",
            "processing_message": None,
            "processing_error": None,
            
            # 匹配状态
            "matching_status": "待匹配",
            "matching_score": None,
            
            # 版本信息
            "resume_version": 1,
            "is_latest": True,
            
            # 来源信息
            "source_channel": None,
            "source_batch": None,
            
            # 质量评分
            "completeness_score": None,
            
            # 项目经历
            "project_experience": analysis_result.get("project_experience", []),
        }
        
        # 确保日期字段格式正确
        date_fields = [
            "birthdate", "graduation_date"
        ]
        for field in date_fields:
            if standardized_data.get(field):
                try:
                    # 确保日期格式为 ISO 格式 (YYYY-MM-DDT00:00:00)
                    if isinstance(standardized_data[field], datetime):
                        standardized_data[field] = (
                            standardized_data[field].strftime(
                                "%Y-%m-%dT%H:%M:%S"
                            )
                        )
                    else:
                        standardized_data[field] = self._parse_date(standardized_data[field])
                except (ValueError, TypeError):
                    standardized_data[field] = None
        
        # 处理工作经历中的日期
        if standardized_data.get("work_history"):
            for work in standardized_data["work_history"]:
                # 处理公司名称
                work["company"] = work.get("company") or "未提供"
                for date_field in ["start_date", "end_date"]:
                    if work.get(date_field):
                        try:
                            if isinstance(work[date_field], datetime):
                                work[date_field] = (
                                    work[date_field].strftime("%Y-%m-%dT%H:%M:%S")
                                )
                            else:
                                work[date_field] = self._parse_date(work[date_field])
                        except (ValueError, TypeError):
                            work[date_field] = None
        
        # 处理教育经历中的日期
        if standardized_data.get("edu_experience"):
            for edu in standardized_data["edu_experience"]:
                for date_field in ["start_date", "end_date"]:
                    if edu.get(date_field):
                        try:
                            if isinstance(edu[date_field], datetime):
                                edu[date_field] = (
                                    edu[date_field].strftime("%Y-%m-%dT%H:%M:%S")
                                )
                            else:
                                edu[date_field] = self._parse_date(edu[date_field])
                        except (ValueError, TypeError):
                            edu[date_field] = None
        
        # 处理项目经历日期
        if standardized_data.get("project_experience"):
            for project in standardized_data["project_experience"]:
                for date_field in ["start_date", "end_date"]:
                    if project.get(date_field):
                        try:
                            if isinstance(project[date_field], datetime):
                                project[date_field] = (
                                    project[date_field].strftime("%Y-%m-%dT%H:%M:%S")
                                )
                            else:
                                project[date_field] = self._parse_date(project[date_field])
                        except (ValueError, TypeError):
                            project[date_field] = None
        
        return standardized_data

    def _parse_date(self, date_str: Optional[str]) -> Optional[str]:
        """解析日期字符串"""
        if not date_str:
            return None
        
        try:
            # 尝试直接解析标准格式的日期字符串
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            return date_obj.strftime("%Y-%m-%dT%H:%M:%S")
        except ValueError:
            try:
                # 尝试解析带时间的日期字符串
                date_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                return date_obj.strftime("%Y-%m-%dT%H:%M:%S")
            except ValueError:
                try:
                    # 尝试解析ISO格式的日期字符串
                    date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
                    return date_obj.strftime("%Y-%m-%dT%H:%M:%S")
                except ValueError:
                    return None

    async def _analyze_resume_with_llm(
        self, 
        resume_text: str,
        llm_config: Any
    ) -> Dict[str, Any]:
        """使用LLM分析简历"""
        system_prompt = self._get_system_prompt()
        prompt = self._get_analysis_prompt(resume_text)
        
        try:
            result = await llm_service.generate_completion(
                prompt=prompt,
                llm_config=llm_config,
                system_prompt=system_prompt
            )
            return json.loads(result["content"])
        except json.JSONDecodeError as e:
            logger.error("Failed to parse LLM response", exc_info=True)
            raise ValueError("简历分析结果格式错误") from e
        except Exception as e:
            logger.error("LLM analysis failed", exc_info=True)
            raise ValueError(f"简历分析失败: {str(e)}") from e

    async def _create_resume_record(
        self,
        db: Session,
        file_info: Dict[str, str],
        resume_data: Dict[str, Any],
        repository_id: int,
        tenant_id: Optional[int]
    ) -> models.Resume:
        """创建简历记录"""
        # 1. 首先创建基础简历记录
        resume = await self.create_resume(
            db,
            file_path=file_info["file_path"],
            repository_id=repository_id,
            original_filename=file_info["file_name"],
            tenant_id=tenant_id
        )
        
        # 2. 处理解析数据
        parsed_data = resume_data["parsed_data"]
        
        # 3. 处理日期格式
        if parsed_data.get('edu_experience'):
            for edu in parsed_data['edu_experience']:
                if edu.get('start_date'):
                    # 添加时间部分
                    edu['start_date'] = f"{edu['start_date']}-01T00:00:00"
                if edu.get('end_date'):
                    edu['end_date'] = f"{edu['end_date']}-01T00:00:00"
        
        # 4. 处理技能和证书
        if parsed_data.get('skills') and isinstance(parsed_data['skills'], dict):
            skills_items = parsed_data['skills'].get('items', [])
            # 创建 SkillInfo 实例
            parsed_data['skills'] = [
                SkillInfo(
                    name=skill,
                    level=None,
                    description=None
                ) for skill in skills_items
            ]
        
        if parsed_data.get('certificates') and isinstance(parsed_data['certificates'], dict):
            cert_items = parsed_data['certificates'].get('items', [])
            # 创建 CertificateInfo 实例
            parsed_data['certificates'] = [
                CertificateInfo(
                    name=cert,
                    issuer=None,
                    issue_date=None,
                    expire_date=None
                ) for cert in cert_items
            ]
        
        # 5. 使用自定义编码器序列化parsed_data
        if parsed_data:
            parsed_data = json.loads(
                self.json_encoder.encode(parsed_data)
            )
        
        # 6. 提取和更新简历字段
        resume_fields = self._extract_resume_fields(parsed_data)
        
        # 7. 使用自定义编码器序列化resume_fields中的JSON字段
        if resume_fields.get('work_history'):
            resume_fields['work_history'] = json.loads(
                self.json_encoder.encode(resume_fields['work_history'])
            )
        if resume_fields.get('edu_experience'):
            resume_fields['edu_experience'] = json.loads(
                self.json_encoder.encode(resume_fields['edu_experience'])
            )
        
        resume = self.update(
            db=db,
            db_obj=resume,
            obj_in=ResumeUpdate(
                content=resume_data["content"],
                parsed_data=parsed_data,
                processing_status="completed",
                **resume_fields
            )
        )
        
        return resume

    def _extract_resume_fields(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """从解析数据中提取简历字段"""
        def convert_to_datetime(date_str: Optional[str]) -> Optional[str]:
            """将日期字符串转换为datetime格式的字符串"""
            if not date_str:
                return None
            
            # 如果已经是datetime对象则转换为字符串
            if isinstance(date_str, datetime):
                return date_str.strftime("%Y-%m-%dT%H:%M:%S")
            
            # 移除可能存在的时间部分
            if "T" in date_str:
                date_str = date_str.split("T")[0]
            
            try:
                # 尝试解析日期字符串
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                return date_obj.strftime("%Y-%m-%dT%H:%M:%S")
            except:
                return None

        # 处理birthdate格式
        birthdate = parsed_data.get("birthdate")
        if birthdate:
            birthdate = convert_to_datetime(birthdate)
        
        # 处理graduation_date格式
        graduation_date = parsed_data.get("graduation_date")
        if graduation_date:
            graduation_date = convert_to_datetime(graduation_date)
        
        # 处理工作经历日期
        work_history = parsed_data.get("work_history", [])
        if work_history:
            for work in work_history:
                # 处理公司名称
                work["company"] = work.get("company") or "未提供"
                if work.get("start_date"):
                    work["start_date"] = convert_to_datetime(work["start_date"])
                if work.get("end_date"):
                    work["end_date"] = convert_to_datetime(work["end_date"])
        
        # 处理教育经历日期
        edu_experience = parsed_data.get("edu_experience", [])
        if edu_experience:
            for edu in edu_experience:
                for date_field in ["start_date", "end_date"]:
                    if edu.get(date_field):
                        try:
                            if isinstance(edu[date_field], datetime):
                                edu[date_field] = (
                                    edu[date_field].strftime("%Y-%m-%dT%H:%M:%S")
                                )
                            else:
                                edu[date_field] = self._parse_date(edu[date_field])
                        except (ValueError, TypeError):
                            edu[date_field] = None

        # 处理项目经历日期
        project_experience = parsed_data.get("project_experience", [])
        if project_experience:
            for project in project_experience:
                for date_field in ["start_date", "end_date"]:
                    if project.get(date_field):
                        try:
                            if isinstance(project[date_field], datetime):
                                project[date_field] = (
                                    project[date_field].strftime("%Y-%m-%dT%H:%M:%S")
                                )
                            else:
                                project[date_field] = self._parse_date(project[date_field])
                        except (ValueError, TypeError):
                            project[date_field] = None

        fields = {
            # 个人基本信息
            "name": parsed_data.get("name"),
            "gender": parsed_data.get("gender"),
            "birthdate": birthdate,
            "id_number": parsed_data.get("id_number"),
            "phone": parsed_data.get("phone"),
            "email": parsed_data.get("email"),
            
            # 个人状态信息
            "political_status": parsed_data.get("political_status"),
            "marital_status": parsed_data.get("marital_status"),
            "hukou": parsed_data.get("hukou"),
            "current_address": parsed_data.get("current_address"),
            
            # 教育信息
            "highest_education": parsed_data.get("highest_education"),
            "highest_degree": parsed_data.get("highest_degree"),
            "major": parsed_data.get("major"),
            "graduate_school": parsed_data.get("graduate_school"),
            "graduation_date": graduation_date,
            
            # 工作经验
            "experience_years": parsed_data.get("experience_years"),
            "current_company": parsed_data.get("current_company"),
            "current_position": parsed_data.get("current_position"),
            "current_salary": parsed_data.get("current_salary"),
            "work_history": work_history,
            
            # 求职意向
            "expected_position": parsed_data.get("expected_position"),
            "expected_salary": parsed_data.get("expected_salary"), 
            "expected_location": parsed_data.get("expected_location"),
            
            # 技能与证书
            "skills": parsed_data.get("skills", []),
            "certificates": parsed_data.get("certificates", []),
            
            # 新增个人基本信息
            "stature": parsed_data.get("stature"),
            "weight": parsed_data.get("weight"),
            "nation": parsed_data.get("nation"),
            "english_level": parsed_data.get("english_level"),
            "city": parsed_data.get("city"),
            "district": parsed_data.get("district"),
            
            # 新增职称信息
            "talent_name": parsed_data.get("talent_name"),
            "talent_team": parsed_data.get("talent_team"),
            "talent_type": parsed_data.get("talent_type"),
            "title_rank": parsed_data.get("title_rank"),
            
            # 新增经历信息
            "edu_experience": edu_experience,
            "project_experience": project_experience,
            "awards": parsed_data.get("awards"),
            
            # 新增其他信息
            "family_situation": parsed_data.get("family_situation"),
            "other_info": parsed_data.get("other_info"),
        }
        
        return {k: v for k, v in fields.items() if v is not None}

    def delete_resume_file(self, file_path: str) -> None:
        """删除简历文件"""
        if not file_path:
            logger.warning("Attempted to delete file with empty file path")
            return
        return self._delete_file(file_path)

    def _delete_file(self, file_path: str) -> None:
        """删除文件"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            logger.error(f"Failed to delete file {file_path}: {str(e)}")

    def delete_resume(self, resume_id: int) -> bool:
        """删除简历"""
        resume = self.get_resume(resume_id)
        if resume:
            self.delete_resume_file(resume.file_path)
            self.db.delete(resume)
            self.db.commit()
            return True
        return False

    def get_resume(self, resume_id: int, db: Session) -> models.Resume:
        """
        获取简历详情
        
        Args:
            resume_id: 简历ID
            db: 数据库会话
            
        Returns:
            models.Resume: 简历对象
            
        Raises:
            HTTPException: 当简历不存在时抛出404错误
        """
        resume = db.query(models.Resume).filter(
            models.Resume.id == resume_id
        ).first()
        if not resume:
            raise HTTPException(status_code=404, detail="简历不存在")
        return resume

    def update_resume(
        self, 
        resume_id: int, 
        resume_update: ResumeUpdate
    ) -> Optional[models.Resume]:
        """更新简历"""
        resume = self.get_resume(resume_id)
        if resume:
            for field, value in resume_update.dict(exclude_unset=True).items():
                setattr(resume, field, value)
            self.db.commit()
            self.db.refresh(resume)
        return resume

    def _get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """你是一个专业的简历分析助手。请从简历文本中提取关键信息，并以JSON格式返回。

请严格按照以下字段结构解析并返回JSON：
{
    "name": "姓名",
    "gender": "性别(M/F)",
    "birthdate": "出生日期(YYYY-MM-DD格式)",
    "id_number": "身份证号",
    "phone": "电话号码",
    "email": "电子邮箱",
    
    "highest_education": "最高学历(如:本科/硕士/博士)",
    "highest_degree": "最高学位(如:学士/硕士/博士)",
    "major": "专业",
    "graduate_school": "毕业院校",
    "graduation_date": "毕业时间(YYYY-MM-DD格式)",
    
    "experience_years": "工作年限(数字)",
    "current_company": "当前公司",
    "current_position": "当前职位",
    "current_salary": "当前薪资",
    
    "stature": "身高",
    "weight": "体重",
    "nation": "民族",
    "english_level": "英语水平",
    "city": "城市",
    "district": "区域",
    
    "talent_name": "人才名称",
    "talent_team": "所属团队",
    "talent_type": "人才类型",
    "title_rank": "职称等级",
    
    "edu_experience": [
        {
            "school": "学校名称",
            "degree": "学位",
            "major": "专业",
            "start_date": "开始时间",
            "end_date": "结束时间"
        }
    ],
    "awards": [
        {
            "name": "奖项名称",
            "level": "奖项级别",
            "date": "获奖时间"
        }
    ],
    
    "family_situation": "家庭情况",
    "other_info": "其他信息",
    "work_history": [
        {
            "company": "公司名称",
            "position": "职位",
            "start_date": "开始时间(YYYY-MM-DD)",
            "end_date": "结束时间(YYYY-MM-DD)",
            "description": "工作描述"
        }
    ],
    
    "project_experience": [
        {
            "name": "项目名称",
            "role": "担任角色",
            "company": "所属公司",
            "start_date": "开始时间(YYYY-MM-DD)",
            "end_date": "结束时间(YYYY-MM-DD)",
            "description": "项目描述",
            "responsibilities": "主要职责",
            "technologies": "使用技术",
            "achievements": "项目成就"
        }
    ],
    
    "expected_position": "期望职位",
    "expected_salary": "期望薪资",
    "expected_location": "期望工作地点",
    
    "skills": [
        {
            "name": "技能名称",
            "level": "技能水平",
            "description": "技能描述"
        }
    ],
    "certificates": [
        {
            "name": "证书名称",
            "issuer": "发证机构",
            "issue_date": "发证日期",
            "expire_date": "到期日期"
        }
    ]
}

解析要求：
1. 日期和年龄处理规则：
   - 所有日期必须转换为YYYY-MM-DD格式
   - 对于只有年月的情况（如"1990年5月"），默认将日设置为"01"
   - 支持多种日期格式的解析：
     * 中文格式：如"1990年5月"、"1990年5月1日"
     * 数字格式：如"1990.5"、"1990.5.1"、"1990/5/1"
     * 英文格式：如"May 1990"、"May 1, 1990"
   - 如果遇到不完整的日期，优先使用"01"作为默认日
   - 如果遇到两位数年份，根据上下文判断世纪（如"90年"可能是1990年）
   - 如果遇到模糊的日期（如"5月"），需要根据上下文推断年份
   - 对于直接标注年龄的情况（如"25岁"、"25周岁"）：
     * 根据简历提交时间或当前时间推算出生年份
     * 默认将出生日期设置为该年的1月1日
     * 如果简历中有其他时间信息（如毕业时间、工作年限），可以结合这些信息更准确地推算出生年份
     * 如果年龄信息不明确（如"20多岁"），需要根据上下文推断最可能的年龄

2. 性别必须使用M/F表示
3. 工作年限必须是数字
4. 如果某字段在简历中未找到，返回null
5. skills和certificates必须按照指定格式返回，包含所有必要字段
6. work_history必须是数组格式，包含工作经历详情

请确保返回的JSON格式正确且可以被解析。"""

    def _get_analysis_prompt(self, resume_text: str) -> str:
        """生成分析提示词"""
        return f"""请分析以下简历文本，提取关键信息并以JSON格式返回：

简历文本：
{resume_text}

请特别注意：
1. 技能信息需要包含 name、level、description 字段
2. 证书信息需要包含 name、issuer、issue_date、expire_date 字段
3. 如果某些字段信息不存在，使用 null 表示

请确保返回的JSON包含所有必需字段，对于无法确定的字段请返回null。"""

    async def parse_resume(self, file_path: str) -> Dict[str, Any]:
        """解析简历内容"""
        # TODO: 实现简历解析逻辑
        return {
            "content": "简历原文内容",
            "name": "张三",
            "email": "zhangsan@example.com",
            "phone": "13800138000",
            "education": {
                "degree": "本科",
                "school": "示例大学",
                "major": "计算机科学"
            },
            "skills": ["Python", "FastAPI", "SQLAlchemy"]
        }

    def get_by_resume_id(self, db: Session, *, resume_id: str) -> Optional[models.Resume]:
        """根据简历ID获取简历"""
        return db.query(models.Resume).filter(
            models.Resume.resume_id == resume_id
        ).first()

    def get_by_repository(self, db: Session, *, repository_id: int) -> List[models.Resume]:
        """获取简历库下的所有简历"""
        return db.query(models.Resume).filter(
            models.Resume.repository_id == repository_id
        ).all()

    def get_by_candidate(self, db: Session, *, candidate_id: int) -> List[models.Resume]:
        """获取候选人的所有简历"""
        return db.query(models.Resume).filter(
            models.Resume.candidate_id == candidate_id
        ).all()

    async def create_resume(
        self,
        db: Session,
        *,
        file_path: str,
        repository_id: int,
        original_filename: str,
        tenant_id: Optional[int] = None,
        publisher_id: Optional[int] = None,
        publisher_type: str = "admin",  # 设置默认发布者类型
        publisher_name: Optional[str] = None
    ) -> models.Resume:
        """创建简历记录"""
        try:
            resume_in = ResumeCreate(
                resume_id=str(uuid.uuid4()),
                repository_id=repository_id,
                tenant_id=tenant_id,
                file_name=original_filename,
                file_path=file_path,
                file_type=file_path.split(".")[-1].lower(),
                processing_status="pending",
                matching_status='待匹配',
                resume_version=1,
                is_latest=True,
                source_channel=None,
                source_batch=None,
                publisher_type=publisher_type,  # 使用传入的发布者类型
                publisher_id=publisher_id,
                publisher_name=publisher_name
            )
            
            return self.create(db=db, obj_in=resume_in)
        except ValidationError as e:
            # 处理验证错误
            error_msg = f"简历数据验证失败: {str(e)}"
            raise HTTPException(
                status_code=422,
                detail=error_msg
            )
        except Exception as e:
            # 处理其他错误
            error_msg = f"创建简历记录失败: {str(e)}"
            raise HTTPException(
                status_code=500,
                detail=error_msg
            )

    async def retry_failed_resume(
        self,
        db: Session,
        *,
        resume_id: str
    ) -> models.Resume:
        """重试失败的简历处理"""
        resume = self.get_by_resume_id(db, resume_id=resume_id)
        if not resume:
            raise HTTPException(status_code=404, detail="简历不存在")
        
        if resume.processing_status != "failed":
            raise HTTPException(status_code=400, detail="只能重试失败的简历")
        
        try:
            # 重新解析简历
            parsed_data = await self.parse_resume(resume.file_path)
            resume_fields = self._extract_resume_fields(parsed_data)
            
            # 更新简历信息
            resume = self.update(
                db=db,
                db_obj=resume,
                obj_in=ResumeUpdate(
                    content=parsed_data.get("content"),
                    parsed_data=parsed_data,
                    processing_status="completed",
                    processing_error=None,
                    **resume_fields
                )
            )
            return resume
            
        except Exception as e:
            # 更新失败状态
            await self.update_resume_status(
                db,
                resume_id=resume_id,
                status="failed",
                error=str(e)
            )
            raise HTTPException(
                status_code=500,
                detail=f"简历重新处理失败: {str(e)}"
            )

    def get_by_status(
        self,
        db: Session,
        *,
        status: str,
        tenant_id: Optional[int] = None
    ) -> List[models.Resume]:
        """获取指定状态的简历"""
        query = db.query(models.Resume).filter(
            models.Resume.processing_status == status
        )
        
        if tenant_id is not None:
            query = query.filter(models.Resume.tenant_id == tenant_id)
            
        return query.all()

    def search_resumes(
        self,
        db: Session,
        *,
        keyword: str,
        tenant_id: Optional[int] = None,
        repository_id: Optional[int] = None,
        status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[models.Resume]:
        """搜索简历"""
        query = db.query(models.Resume)
        
        # 基础过滤条件
        filters = []
        if tenant_id is not None:
            filters.append(models.Resume.tenant_id == tenant_id)
        if repository_id is not None:
            filters.append(models.Resume.repository_id == repository_id)
        if status:
            filters.append(models.Resume.processing_status == status)
        if start_date:
            filters.append(models.Resume.created_at >= start_date)
        if end_date:
            filters.append(models.Resume.created_at <= end_date)
            
        # 关键词搜索
        if keyword:
            # 对于普通文本字段使用ILIKE
            text_fields_filter = or_(
                models.Resume.name.ilike(f"%{keyword}%"),
                models.Resume.email.ilike(f"%{keyword}%"),
                models.Resume.phone.ilike(f"%{keyword}%"),
                models.Resume.content.ilike(f"%{keyword}%"),
                models.Resume.major.ilike(f"%{keyword}%"),
                models.Resume.graduate_school.ilike(f"%{keyword}%")
            )
            
            # 对于JSON类型的skills字段，使用PostgreSQL的JSON操作符
            # 使用::text将JSON转换为文本，然后使用ILIKE
            skills_filter = models.Resume.skills.cast(String).ilike(f"%{keyword}%")
            
            # 合并所有过滤条件
            keyword_filter = or_(text_fields_filter, skills_filter)
            filters.append(keyword_filter)
            
        if filters:
            query = query.filter(and_(*filters))
            
        return query.offset(skip).limit(limit).all()

    async def link_to_candidate(
        self,
        db: Session,
        *,
        resume_id: str,
        candidate_id: int
    ) -> models.Resume:
        """将简历关联到候选人"""
        resume = self.get_by_resume_id(db, resume_id=resume_id)
        if not resume:
            raise HTTPException(status_code=404, detail="简历不存在")
            
        candidate = crud.candidate.get(db, id=candidate_id)
        if not candidate:
            raise HTTPException(status_code=404, detail="候选人不存在")
            
        # 检查租户一致性
        if resume.tenant_id != candidate.tenant_id:
            raise HTTPException(status_code=400, detail="简历与候选人不属于同一租户")
            
        resume = self.update(
            db,
            db_obj=resume,
            obj_in=ResumeUpdate(candidate_id=candidate_id)
        )
        return resume

    async def move_to_repository(
        self,
        db: Session,
        *,
        resume_id: str,
        target_repository_id: int
    ) -> models.Resume:
        """将简历移动到其他简历库"""
        resume = self.get_by_resume_id(db, resume_id=resume_id)
        if not resume:
            raise HTTPException(status_code=404, detail="简历不存在")
            
        target_repo = repository_service.get_by_name(
            db, 
            id=target_repository_id,
            tenant_id=resume.tenant_id
        )
        if not target_repo:
            raise HTTPException(status_code=404, detail="目标简历库不存在")
            
        # 检查租户一致性
        if resume.tenant_id != target_repo.tenant_id:
            raise HTTPException(status_code=400, detail="简历与目标简历库不属于同一租户")
            
        # 移动文件
        old_path = resume.file_path
        new_path = os.path.join(
            settings.UPLOAD_DIR,
            str(target_repository_id),
            os.path.basename(old_path)
        )
        
        os.makedirs(os.path.dirname(new_path), exist_ok=True)
        os.rename(old_path, new_path)
        
        # 更新简历记录
        resume = self.update(
            db,
            db_obj=resume,
            obj_in=ResumeUpdate(
                repository_id=target_repository_id,
                file_path=new_path
            )
        )
        return resume

    async def batch_delete_resumes(
        self,
        db: Session,
        *,
        resume_ids: List[str],
        tenant_id: int
    ) -> None:
        """批量删除简历"""
        for resume_id in resume_ids:
            resume = self.get_by_resume_id(db, resume_id=resume_id)
            if not resume:
                continue
                
            # 检查租户权限
            if resume.tenant_id != tenant_id:
                raise HTTPException(
                    status_code=403,
                    detail=f"无权删除简历 {resume_id}"
                )
                
            # 删除文件和记录
            self._delete_file(resume.file_path)
            self.remove(db=db, id=resume.id)

    async def analyze_resume(
        self,
        db: Session,
        *,
        resume_id: str,
        llm_config_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """使用LLM分析简历内容"""
        from app.services import llm_config_service
        
        resume = self.get_by_resume_id(db, resume_id=resume_id)
        if not resume:
            raise HTTPException(status_code=404, detail="简历不存在")
            
        # 获取LLM配置
        if llm_config_id:
            llm_config = llm_config_service.get_config(db, id=llm_config_id)
            if not llm_config:
                raise HTTPException(status_code=404, detail="LLM配置不存在")
        else:
            llm_config = llm_config_service.get_default_config_by_tenant(
                db,
                tenant_id=resume.tenant_id
            )
            if not llm_config:
                raise HTTPException(status_code=404, detail="未找到默认LLM配置")
        
        try:
            # TODO: 实现LLM分析逻辑
            analysis_result = {
                "summary": "候选人概述...",
                "skills_match": ["技能匹配分析..."],
                "experience_evaluation": "工作经验评估...",
                "education_evaluation": "教育背景评估...",
                "recommendations": ["建议..."]
            }
            
            # 更新简历分析结果
            resume = self.update(
                db,
                db_obj=resume,
                obj_in=ResumeUpdate(
                    analysis_result=analysis_result,
                    analyzed_at=datetime.utcnow()
                )
            )
            
            return analysis_result
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"简历分析失败: {str(e)}"
            )

    async def match_jobs(
        self,
        db: Session,
        *,
        resume_id: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """匹配适合的职位"""
        resume = self.get_by_resume_id(db, resume_id=resume_id)
        if not resume:
            raise HTTPException(status_code=404, detail="简历不存在")
        
        # 获取同一租户下的所有职位
        jobs = db.query(models.Job).filter(
            models.Job.tenant_id == resume.tenant_id,
            models.Job.status == "active"
        ).all()
        
        matches = []
        for job in jobs:
            # TODO: 实现职位匹配算法
            match_score = 0.0  # 计算匹配度
            
            matches.append({
                "job_id": job.id,
                "job_title": job.title,
                "match_score": match_score,
                "match_reasons": ["匹配原因..."]
            })
        
        # 按匹配度排序并返回前N个
        matches.sort(key=lambda x: x["match_score"], reverse=True)
        return matches[:limit]

    async def export_resumes(
        self,
        db: Session,
        *,
        resume_ids: List[str],
        export_format: str = "pdf"
    ) -> str:
        """导出简历"""
        if export_format not in ["pdf", "docx"]:
            raise HTTPException(status_code=400, detail="不支持的导出格式")
        
        # 创建导出目录
        export_dir = os.path.join(settings.EXPORT_DIR, str(uuid.uuid4()))
        os.makedirs(export_dir, exist_ok=True)
        
        try:
            exported_files = []
            for resume_id in resume_ids:
                resume = self.get_by_resume_id(db, resume_id=resume_id)
                if not resume:
                    continue
                
                # TODO: 实现文件格式转换逻辑
                # 注释掉未使用的变量
                # source_file = resume.file_path
                target_file = os.path.join(
                    export_dir,
                    f"{resume.name}_{resume_id}.{export_format}"
                )
                
                # 转换文件格式
                # convert_file(source_file, target_file, export_format)
                exported_files.append(target_file)
            
            if not exported_files:
                raise HTTPException(status_code=404, detail="未找到要导出的简历")
            
            # 如果只有一个文件,直接返回文件路径
            if len(exported_files) == 1:
                return exported_files[0]
            
            # 多个文件打包成zip
            zip_file = f"{export_dir}.zip"
            import zipfile
            with zipfile.ZipFile(zip_file, 'w') as zf:
                for file in exported_files:
                    zf.write(file, os.path.basename(file))
            
            return zip_file
            
        except Exception as e:
            # 清理临时文件
            if os.path.exists(export_dir):
                shutil.rmtree(export_dir)
            raise HTTPException(
                status_code=500,
                detail=f"导出失败: {str(e)}"
            )

    async def get_resume_statistics(
        self,
        db: Session,
        *,
        tenant_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """获取简历统计信息"""
        query = db.query(models.Resume)
        
        if tenant_id is not None:
            query = query.filter(models.Resume.tenant_id == tenant_id)
        if start_date:
            query = query.filter(models.Resume.created_at >= start_date)
        if end_date:
            query = query.filter(models.Resume.created_at <= end_date)
            
        total_resumes = query.count()
        processed_resumes = query.filter(
            models.Resume.processing_status == "completed"
        ).count()
        failed_resumes = query.filter(
            models.Resume.processing_status == "failed"
        ).count()
        pending_resumes = query.filter(
            models.Resume.processing_status == "pending"
        ).count()
        
        # 按学历统计
        education_stats = (
            query.filter(models.Resume.highest_education.isnot(None))
            .with_entities(
                models.Resume.highest_education,
                db.func.count(models.Resume.id)
            )
            .group_by(models.Resume.highest_education)
            .all()
        )
        
        # 按技能统计
        skills_stats = {}
        resumes_with_skills = query.filter(
            models.Resume.skills.isnot(None)
        ).all()
        for resume in resumes_with_skills:
            for skill in resume.skills:
                skills_stats[skill] = skills_stats.get(skill, 0) + 1
                
        return {
            "total_resumes": total_resumes,
            "processed_resumes": processed_resumes,
            "failed_resumes": failed_resumes,
            "pending_resumes": pending_resumes,
            "education_distribution": dict(education_stats),
            "top_skills": dict(
                sorted(
                    skills_stats.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:10]
            )
        }

    async def merge_duplicate_resumes(
        self,
        db: Session,
        *,
        resume_ids: List[str],
        tenant_id: int
    ) -> models.Resume:
        """合并重复的简历"""
        if len(resume_ids) < 2:
            raise HTTPException(
                status_code=400,
                detail="需要至少两个简历进行合并"
            )
            
        resumes = []
        for resume_id in resume_ids:
            resume = self.get_by_resume_id(db, resume_id=resume_id)
            if not resume:
                continue
                
            # 检查租户权限
            if resume.tenant_id != tenant_id:
                raise HTTPException(
                    status_code=403,
                    detail=f"无权访问简历 {resume_id}"
                )
            resumes.append(resume)
            
        if len(resumes) < 2:
            raise HTTPException(
                status_code=400,
                detail="未找到足够的有效简历进行合并"
            )
            
        # 以最新的简历为主
        primary_resume = max(resumes, key=lambda x: x.created_at)
        other_resumes = [r for r in resumes if r.id != primary_resume.id]
        
        try:
            # 更新主简历信息
            merged_data = {
                "merged_from": [r.resume_id for r in other_resumes],
                "merged_at": datetime.utcnow()
            }
            
            # 合并解析数据
            if primary_resume.parsed_data:
                merged_data["parsed_data"] = primary_resume.parsed_data
                for resume in other_resumes:
                    if resume.parsed_data:
                        # TODO: 实现数据合并逻辑
                        pass
            
            # 更新主简历
            primary_resume = self.update(
                db,
                db_obj=primary_resume,
                obj_in=ResumeUpdate(**merged_data)
            )
            
            # 删除其他简历
            for resume in other_resumes:
                self._delete_file(resume.file_path)
                self.remove(db=db, id=resume.id)
                
            return primary_resume
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"简历合并失败: {str(e)}"
            )

    async def check_duplicate_resumes(
        self,
        db: Session,
        *,
        resume_id: str,
        tenant_id: int,
        threshold: float = 0.8
    ) -> List[Dict[str, Any]]:
        """检查重复简历"""
        resume = self.get_by_resume_id(db, resume_id=resume_id)
        if not resume:
            raise HTTPException(status_code=404, detail="简历不存在")
            
        # 获取同一租户下的其他简历
        other_resumes = db.query(models.Resume).filter(
            models.Resume.tenant_id == tenant_id,
            models.Resume.id != resume.id
        ).all()
        
        duplicates = []
        for other in other_resumes:
            # TODO: 实现相似度计算逻辑
            similarity = 0.0
            
            if similarity >= threshold:
                duplicates.append({
                    "resume_id": other.resume_id,
                    "similarity": similarity,
                    "created_at": other.created_at,
                    "file_name": other.file_name
                })
                
        return sorted(duplicates, key=lambda x: x["similarity"], reverse=True)

    async def analyze_resume_with_llm(
        self,
        db: Session,
        *,
        resume_id: str,
        llm_config_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """使用LLM分析简历内容"""
        resume = self.get_by_resume_id(db, resume_id=resume_id)
        if not resume:
            raise HTTPException(status_code=404, detail="简历不存在")
            
        # 获取LLM配置
        if llm_config_id:
            llm_config = llm_config_service.get_config(db, id=llm_config_id)
            if not llm_config:
                raise HTTPException(status_code=404, detail="LLM配置不存在")
        else:
            llm_config = llm_config_service.get_default_config_by_tenant(
                db,
                tenant_id=resume.tenant_id
            )
            if not llm_config:
                raise HTTPException(status_code=404, detail="未找到默认LLM配置")
        
        try:
            # TODO: 实现LLM分析逻辑
            analysis_result = {
                "summary": "候选人概述...",
                "skills_match": ["技能匹配分析..."],
                "experience_evaluation": "工作经验评估...",
                "education_evaluation": "教育背景评估...",
                "recommendations": ["建议..."]
            }
            
            # 更新简历分析结果
            resume = self.update(
                db,
                db_obj=resume,
                obj_in=ResumeUpdate(
                    llm_analysis=analysis_result,
                    llm_analyzed_at=datetime.utcnow(),
                    llm_config_id=llm_config.id
                )
            )
            
            return analysis_result
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"简历分析失败: {str(e)}"
            )

    async def batch_analyze_resumes(
        self,
        db: Session,
        *,
        resume_ids: List[str],
        llm_config_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """批量分析简历"""
        results = {
            "total": len(resume_ids),
            "success": 0,
            "failed": 0,
            "failed_ids": []
        }
        
        for resume_id in resume_ids:
            try:
                await self.analyze_resume_with_llm(
                    db,
                    resume_id=resume_id,
                    llm_config_id=llm_config_id
                )
                results["success"] += 1
            except Exception as e:
                results["failed"] += 1
                results["failed_ids"].append({
                    "resume_id": resume_id,
                    "error": str(e)
                })
                
        return results

    async def get_resume_analysis_history(
        self,
        db: Session,
        *,
        resume_id: str
    ) -> List[Dict[str, Any]]:
        """获取简历分析历史"""
        resume = self.get_by_resume_id(db, resume_id=resume_id)
        if not resume:
            raise HTTPException(status_code=404, detail="简历不存在")
            
        # 获取分析历史记录
        history = db.query(models.ResumeAnalysisHistory).filter(
            models.ResumeAnalysisHistory.resume_id == resume.id
        ).order_by(
            models.ResumeAnalysisHistory.created_at.desc()
        ).all()
        
        return [
            {
                "analysis_id": h.id,
                "llm_config_id": h.llm_config_id,
                "analysis_result": h.analysis_result,
                "created_at": h.created_at
            }
            for h in history
        ]

    async def compare_resume_versions(
        self,
        db: Session,
        *,
        resume_id: str,
        version1_id: int,
        version2_id: int
    ) -> Dict[str, Any]:
        """比较简历分析版本"""
        resume = self.get_by_resume_id(db, resume_id=resume_id)
        if not resume:
            raise HTTPException(status_code=404, detail="简历不存在")
            
        # 获取两个版本的分析结果
        v1 = db.query(models.ResumeAnalysisHistory).get(version1_id)
        v2 = db.query(models.ResumeAnalysisHistory).get(version2_id)
        
        if not v1 or not v2:
            raise HTTPException(status_code=404, detail="分析版本不存在")
            
        # TODO: 实现版本比较逻辑
        comparison = {
            "summary_diff": "差异概述...",
            "skills_changes": ["技能变化..."],
            "experience_changes": "经验变化...",
            "education_changes": "教育背景变化...",
            "overall_evaluation": "总体评估..."
        }
        
        return comparison

    @staticmethod
    async def update_resume_matching_status(
        db: Session, 
        resume_id: int, 
        status: str,
        matching_score: Optional[int] = None
    ) -> models.Resume:
        resume = db.query(models.Resume).filter(models.Resume.id == resume_id).first()
        if resume:
            resume.matching_status = status
            if matching_score is not None:
                resume.matching_score = matching_score
            db.commit()
            db.refresh(resume)
        return resume

    @staticmethod
    async def update_resume_version(
        db: Session,
        old_resume_id: int,
        new_resume: ResumeCreate
    ) -> models.Resume:
        # 将旧简历标记为非最新
        old_resume = db.query(models.Resume).filter(models.Resume.id == old_resume_id).first()
        if old_resume:
            old_resume.is_latest = False
            
        # 创建新版本简历
        # 注释掉未使用的变量
        # new_resume_version = old_resume.resume_version + 1 if old_resume else 1
        # db_resume = models.Resume(
        #     # ... existing fields ...
        #     resume_version=new_resume_version,
        #     is_latest=True
        # )
        # ... existing code ...

    async def approve_resume(
        self,
        db: Session,
        resume_id: int,
        reviewer_id: int,
        comment: Optional[str] = None
    ) -> models.Resume:
        """审核通过简历"""
        resume = crud.resume.get(db, id=resume_id)
        if not resume:
            raise ValueError("简历不存在")
        
        resume_update = ResumeUpdate(
            review_status="approved",
            reviewer_id=reviewer_id,
            review_comment=comment
        )
        
        return crud.resume.update(db, db_obj=resume, obj_in=resume_update)

    async def reject_resume(
        self,
        db: Session,
        resume_id: int,
        reviewer_id: int,
        comment: str
    ) -> models.Resume:
        """拒绝简历"""
        resume = crud.resume.get(db, id=resume_id)
        if not resume:
            raise ValueError("简历不存在")
        
        resume_update = ResumeUpdate(
            review_status="rejected",
            reviewer_id=reviewer_id,
            review_comment=comment
        )
        
        return crud.resume.update(db, db_obj=resume, obj_in=resume_update)

    async def publish_resume(
        self,
        db: Session,
        resume_id: int,
        publisher_id: int,
        publisher_type: str,
        publisher_name: str
    ) -> models.Resume:
        """发布简历"""
        resume = crud.resume.get(db, id=resume_id)
        if not resume:
            raise ValueError("简历不存在")
        
        resume_update = ResumeUpdate(
            publisher_id=publisher_id,
            publisher_type=publisher_type,
            publisher_name=publisher_name
        )
        
        return crud.resume.update(db, db_obj=resume, obj_in=resume_update)

    async def process_resume_file_with_form_data(
        self,
        db: Session,
        file: UploadFile,
        repository_id: int,
        tenant_id: int,
        publisher_id: int = None,
        publisher_type: str = None,
        publisher_name: str = None,
        form_data: Dict[str, Any] = None
    ) -> models.Resume:
        """处理上传的简历文件和表单数据"""
        try:
            # 保存文件
            file_info = await self._save_file(file, repository_id)
            
            # 解析和分析简历
            resume_data = await self._parse_and_analyze_resume(db, file_info)
            
            logger.info(f"解析和分析简历: {pformat(resume_data)}")
            
            # 创建简历记录
            resume_data["repository_id"] = repository_id
            resume_data["tenant_id"] = tenant_id
            resume_data["resume_id"] = str(uuid.uuid4())
            resume_data["processing_status"] = "pending"
            resume_data["publisher_id"] = publisher_id
            resume_data["publisher_type"] = publisher_type
            resume_data["publisher_name"] = publisher_name
            resume_data["review_status"] = "pending"
            
            # 合并表单数据（表单数据优先级高于解析数据）
            if form_data:
                # 更新基本字段
                for key, value in form_data.items():
                    if key in resume_data:
                        resume_data[key] = value
                    elif key in resume_data.get("parsed_data", {}):
                        resume_data["parsed_data"][key] = value
            
            resume_in = ResumeCreate(**resume_data)
            resume = self.create(db=db, obj_in=resume_in)
            
            return resume
            
        except Exception as e:
            # 清理文件
            if 'file_info' in locals() and file_info.get('file_path'):
                self._delete_file(file_info['file_path'])
            logger.error(f"Resume processing failed: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"简历处理失败: {str(e)}"
            )

    def validate_resume_data(self, resume_data: dict) -> tuple[bool, str]:
        """验证简历数据的有效性
        
        Args:
            resume_data: 简历数据字典
            
        Returns:
            (is_valid, error_message): 验证结果和错误信息
        """
        # 验证必填字段 - 不再要求repository_id
        # required_fields = ["repository_id"]
        # for field in required_fields:
        #     if field not in resume_data or resume_data[field] is None:
        #         return False, f"缺少必填字段: {field}"
        
        # 验证联系方式（至少有一种联系方式）
        contact_fields = ["phone", "email"]
        has_contact = any(resume_data.get(field) for field in contact_fields)
        if not has_contact:
            return False, "至少需要提供一种联系方式（电话或邮箱）"
        
        # 验证工作经历的时间范围
        if "work_history" in resume_data and resume_data["work_history"]:
            for work in resume_data["work_history"]:
                if (work.get("start_date") and work.get("end_date") and 
                        work["start_date"] > work["end_date"]):
                    return False, "工作经历的开始时间不能晚于结束时间"
        
        # 验证教育经历的时间范围
        if "edu_experience" in resume_data and resume_data["edu_experience"]:
            for edu in resume_data["edu_experience"]:
                if (edu.get("start_date") and edu.get("end_date") and 
                        edu["start_date"] > edu["end_date"]):
                    return False, "教育经历的开始时间不能晚于结束时间"
        
        return True, ""

    def create(
        self,
        db: Session,
        *,
        obj_in: ResumeCreate
    ) -> models.Resume:
        """创建简历记录
        
        重写 BaseService 的 create 方法，避免使用 self.model
        """
        try:
            # 将 Pydantic 模型转换为字典
            obj_in_data = obj_in.model_dump()
            
            # 创建 ORM 模型实例
            db_obj = models.Resume(**obj_in_data)
            
            # 添加到数据库
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            
            return db_obj
        except Exception as e:
            db.rollback()
            raise ValueError(f"创建简历失败: {str(e)}") from e

    def get_resumes_with_filters(
        self,
        db: Session,
        *,
        tenant_id: Optional[int] = None,
        filters: dict,
        skip: int = 0,
        limit: int = 100
    ) -> List[models.Resume]:
        """获取带过滤条件的简历列表"""
        return crud.resume.get_multi_with_filters(
            db=db,
            tenant_id=tenant_id,
            filters=filters,
            skip=skip,
            limit=limit
        )

    def get_resumes_count_with_filters(
        self,
        db: Session,
        *,
        tenant_id: Optional[int] = None,
        filters: dict
    ) -> int:
        """获取带过滤条件的简历总数"""
        return crud.resume.get_multi_with_filters_count(
            db=db,
            tenant_id=tenant_id,
            filters=filters
        )

    def prepare_resume_data(
        self,
        resume_data: dict,
        current_user: models.User
    ) -> dict:
        """准备简历数据，添加发布者信息等"""
        # 确保生成resume_id
        if not resume_data.get("resume_id"):
            # 使用更短的时间戳格式
            timestamp = str(int(time.time()))[-6:]  # 取时间戳后6位
            random_num = str(random.randint(1000, 9999))
            resume_data["resume_id"] = f"R{timestamp}{random_num}"
        
        # 设置发布者信息
        publisher_type = current_user.user_type if current_user.user_type else "admin"
        resume_data.update({
            "publisher_id": current_user.id,
            "publisher_type": publisher_type,  # 确保publisher_type不为空
            "publisher_name": current_user.username,
            "tenant_id": current_user.tenant_id
        })
        
        # 设置手动创建标志
        if not resume_data.get("file_path"):
            resume_data["is_manual_entry"] = True
        
        return resume_data

    def validate_repository_access(
        self,
        db: Session,
        repository_id: int,
        tenant_id: int,
        is_superuser: bool
    ) -> None:
        """验证简历库访问权限"""
        if not repository_id:
            return
        
        # 修改为使用 get 方法
        repository = repository_service.get(db, id=repository_id)
        if not repository:
            raise ValueError("简历库不存在")
        
        if not is_superuser and repository.tenant_id != tenant_id:
            raise ValueError("无权访问该简历库")

    def create_resume_with_job(
        self,
        db: Session,
        *,
        resume_data: dict,
        current_user: models.User,
        job_id: Optional[int] = None,
        job_external_id: Optional[str] = None,
        background_tasks: Optional[BackgroundTasks] = None
    ) -> models.Resume:
        """创建简历并关联职位"""
        try:
            # 准备简历数据，确保包含resume_id
            resume_data = self.prepare_resume_data(resume_data, current_user)
            
            # 验证简历数据
            is_valid, error_message = self.validate_resume_data(resume_data)
            if not is_valid:
                raise ValueError(error_message)
            
            # 验证简历库权限
            try:
                self.validate_repository_access(
                    db,
                    resume_data.get("repository_id"),
                    current_user.tenant_id,
                    current_user.is_superuser
                )
            except ValueError as e:
                raise ValueError(str(e))
            
            # 创建简历
            resume_obj = schemas.ResumeCreate(**resume_data)
            resume = self.create(db=db, obj_in=resume_obj)
            
            # 处理职位申请
            if job_id or job_external_id:
                job = None
                if job_id:
                    # 直接使用 crud.job 来获取职位
                    job = crud.job.get(db=db, id=job_id)
                elif job_external_id:
                    # 使用查询来获取职位
                    job = db.query(models.Job).filter(
                        models.Job.external_id == job_external_id
                    ).first()
                
                if job:
                    if (job.tenant_id != current_user.tenant_id and 
                            not current_user.is_superuser):
                        raise ValueError("无权访问该职位")
                        
                    job_application = schemas.JobApplicationCreate(
                        job_id=job.id,
                        resume_id=resume.id,
                        status="pending",
                        tenant_id=current_user.tenant_id,
                        created_by=current_user.id
                    )
                    
                    if background_tasks:
                        # 在函数内部导入以避免循环导入
                        from app.services.job_application_service import job_application_service
                        background_tasks.add_task(
                            job_application_service.create_application_with_validation,
                            db=db,
                            application_in=job_application,
                            tenant_id=current_user.tenant_id,
                            created_by=current_user.id
                        )
                
            return resume
            
        except Exception as e:
            logger.error(f"创建简历失败: {str(e)}", exc_info=True)
            raise ValueError(f"创建简历失败: {str(e)}")

    async def convert_to_pdf(self, file_path: str) -> Optional[str]:
        """将Word文档转换为PDF
        
        Args:
            file_path: Word文档路径
            
        Returns:
            转换后的PDF文件路径，如果转换失败则返回None
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                logger.error(f"文件不存在: {file_path}")
                return None

            # 获取文件扩展名
            file_ext = Path(file_path).suffix.lower()
            if file_ext not in ['.doc', '.docx']:
                logger.error(f"不支持的文件类型: {file_ext}")
                return None

            # 生成输出PDF路径
            pdf_filename = f"{uuid.uuid4()}.pdf"
            pdf_path = os.path.join(self.conversion_dir, pdf_filename)

            # 使用LibreOffice进行转换
            process = subprocess.Popen(
                ['soffice', '--headless', '--convert-to', 'pdf', 
                 '--outdir', self.conversion_dir, file_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # 等待转换完成
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                logger.error(f"转换失败: {stderr.decode()}")
                return None

            if not os.path.exists(pdf_path):
                logger.error("转换后的PDF文件不存在")
                return None

            return pdf_path

        except Exception as e:
            logger.error(f"文件转换异常: {str(e)}", exc_info=True)
            return None

    async def get_preview_url(
        self,
        db: Session,
        resume_id: str
    ) -> Dict[str, Any]:
        """获取简历预览URL
        
        Args:
            db: 数据库会话
            resume_id: 简历ID
            
        Returns:
            包含预览URL和文件类型的字典
        """
        resume = self.get_by_resume_id(db, resume_id=resume_id)
        if not resume:
            raise HTTPException(status_code=404, detail="简历不存在")

        if not resume.file_path or not os.path.exists(resume.file_path):
            raise HTTPException(status_code=404, detail="简历文件不存在")

        file_ext = Path(resume.file_path).suffix.lower()
        
        # 如果是Word文档，转换为PDF
        if file_ext in ['.doc', '.docx']:
            pdf_path = await self.convert_to_pdf(resume.file_path)
            if not pdf_path:
                raise HTTPException(
                    status_code=500,
                    detail="文件转换失败"
                )
            preview_path = pdf_path
        else:
            preview_path = resume.file_path

        # 生成预览URL
        return {
            "url": f"/api/resume/preview/{resume_id}",
            "fileType": "pdf" if file_ext in ['.doc', '.docx'] else file_ext[1:]
        }

    def cleanup_conversion_files(self):
        """清理转换的临时文件"""
        try:
            # 删除超过24小时的转换文件
            current_time = time.time()
            for file_name in os.listdir(self.conversion_dir):
                file_path = os.path.join(self.conversion_dir, file_name)
                if os.path.isfile(file_path):
                    # 获取文件的最后修改时间
                    file_time = os.path.getmtime(file_path)
                    # 如果文件超过24小时
                    if current_time - file_time > 24 * 3600:
                        os.remove(file_path)
        except Exception as e:
            logger.error(f"清理转换文件失败: {str(e)}", exc_info=True)

    async def quick_save_file(self, file: UploadFile) -> Dict[str, str]:
        """快速保存文件，返回文件信息"""
        try:
            # 1. 生成唯一文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4().hex[:8])
            original_filename = file.filename
            file_ext = os.path.splitext(original_filename)[1].lower()
            new_filename = f"{timestamp}_{unique_id}{file_ext}"
            
            # 2. 准备保存路径
            save_dir = os.path.join(settings.UPLOAD_DIR, "temp")
            os.makedirs(save_dir, exist_ok=True)
            file_path = os.path.join(save_dir, new_filename)
            
            # 3. 异步保存文件
            async with aiofiles.open(file_path, 'wb') as f:
                while chunk := await file.read(8192):  # 每次读取 8KB
                    await f.write(chunk)
            
            # 4. 返回文件信息
            return {
                "file_path": file_path,
                "file_name": original_filename,
                "file_type": file_ext[1:] if file_ext else "",
                "file_size": os.path.getsize(file_path)
            }
            
        except Exception as e:
            logger.error(f"保存文件失败: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"保存文件失败: {str(e)}"
            )

    async def create_initial_resume(
        self,
        db: Session,
        file_info: Dict[str, str],
        repository_id: Optional[int],
        current_user: models.User,
        job_id: Optional[int] = None
    ) -> models.Resume:
        """快速创建初始简历记录"""
        try:
            # 1. 准备基础数据
            resume_data = {
                "file_path": file_info["file_path"],
                "file_name": file_info["file_name"],
                "file_type": file_info["file_type"],
                "repository_id": repository_id,
                "tenant_id": current_user.tenant_id,
                "resume_id": str(uuid.uuid4()),
                "processing_status": "pending",
                "review_status": "pending",
                "is_latest": True,
                "resume_version": 1,
                "created_by": current_user.id,
                "updated_by": current_user.id,
                "publisher_type": current_user.user_type or "admin",  # 设置发布者类型
                "publisher_id": current_user.id,  # 设置发布者ID
                "publisher_name": current_user.username  # 设置发布者名称
            }
            
            # 2. 创建简历记录
            resume_in = ResumeCreate(**resume_data)
            resume = self.create(db=db, obj_in=resume_in)
            
            # 3. 如果有关联职位，创建关联
            if job_id:
                job = job_service.get_job(db=db, job_id=job_id)
                if job:
                    resume.job_id = job_id
                    db.commit()
                    db.refresh(resume)
            
            return resume
            
        except Exception as e:
            logger.error(f"创建简历记录失败: {str(e)}")
            # 删除已上传的文件
            if file_info and file_info.get("file_path"):
                try:
                    os.unlink(file_info["file_path"])
                except Exception as del_e:
                    logger.error(f"删除文件失败: {str(del_e)}")
            raise HTTPException(
                status_code=500,
                detail=f"创建简历记录失败: {str(e)}"
            )

    async def async_process_resume(
        self,
        resume_id: int,
        publisher_id: int, 
        job_id: Optional[int] = None,
        job_external_id: Optional[str] = None
    ) -> None:
        """异步处理简历内容"""
        # 创建新的数据库会话
        db = SessionLocal()
        try:
            # 1. 获取简历记录
            resume = db.query(models.Resume).filter(
                models.Resume.id == resume_id
            ).first()
            
            if not resume:
                logger.error(f"简历不存在: {resume_id}")
                return
                
            try:
                # 2. 解析文件
                resume_text = await parser_service.parse_resume(resume.file_path)
                
                # 3. 获取LLM配置
                llm_config = await llm_service.get_default_config(db)
                
                # 4. 分析简历内容
                analysis_result = await self._analyze_resume_with_llm(resume_text, llm_config)
                
                # 5. 更新简历记录
                resume.content = resume_text
                resume.parsed_data = analysis_result
                resume.processing_status = "completed"
                resume.processing_error = None
                resume.updated_at = datetime.utcnow()
                
                # 6. 更新基本字段
                resume_fields = self._extract_resume_fields(analysis_result)
                for field, value in resume_fields.items():
                    if hasattr(resume, field):
                        setattr(resume, field, value)
                
                logger.debug("job_id: %s, job_external_id: %s", job_id, job_external_id)
                # 处理职位申请
                job = None
                if job_id or job_external_id:
                    if job_id:
                        job = job_service.get_job(db=db, job_id=job_id)
                    elif job_external_id:
                        job = db.query(models.Job).filter(
                            models.Job.external_id == job_external_id
                        ).first()
                
                if job:
                    # 检查当前用户是否有权限访问该职位
                    current_user = db.query(models.User).filter(
                        models.User.id == publisher_id
                    ).first()
                    if not current_user:
                        logger.error(f"用户不存在: {publisher_id}")
                        return
                    if (job.tenant_id != current_user.tenant_id and 
                            not current_user.is_superuser):
                        raise ValueError("无权访问该职位")
                        
                    job_application = schemas.JobApplicationCreate(
                        job_id=job.id,
                        resume_id=resume.id,
                        status="pending",
                        tenant_id=current_user.tenant_id,
                        created_by=current_user.id
                    )
                    
                    # 直接创建职位申请
                    from app.services.job_application_service import job_application_service
                    await job_application_service.create_application_with_validation(
                        db=db,
                        application_in=job_application,
                        tenant_id=current_user.tenant_id,
                        created_by=current_user.id
                    )
                
                # 7. 提交更改
                db.commit()
                
                # 8. 记录日志
                logger.info(f"简历 {resume_id} 处理完成")
                
            except Exception as e:
                logger.error(f"处理简历失败: {str(e)}")
                resume.processing_status = "failed"
                resume.processing_error = str(e)
                db.commit()
                
        except Exception as e:
            logger.error(f"数据库操作失败: {str(e)}")
            db.rollback()
        finally:
            db.close()
            
    def process_resume_sync(
        self,
        resume_id: int,
        publisher_id: int, 
        job_id: Optional[int] = None,
        job_external_id: Optional[str] = None
    ) -> None:
        """同步处理简历内容，用于 Celery 任务"""
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self.async_process_resume(
                resume_id=resume_id,
                publisher_id=publisher_id,
                job_id=job_id,
                job_external_id=job_external_id
            )
        )

    async def _parse_resume(self, file_path: str) -> str:
        """解析简历文件内容"""
        try:
            # 根据文件类型选择解析方法
            file_ext = file_path.split(".")[-1].lower()
            return await parser_service.parse_resume(file_path)
        except Exception as e:
            logger.error(f"解析简历文件失败: {str(e)}")
            raise

    async def _analyze_resume(self, resume_text: str) -> Dict[str, Any]:
        """分析简历内容"""
        try:
            # 使用LLM分析简历内容
            analysis_result = await llm_service.analyze_resume(resume_text)
            return analysis_result
        except Exception as e:
            logger.error(f"分析简历内容失败: {str(e)}")
            raise

    async def _update_resume_content(
        self,
        db: Session,
        resume_id: int,
        resume_text: str,
        analysis_result: Dict[str, Any]
    ) -> None:
        """更新简历内容"""
        try:
            resume = db.query(models.Resume).filter(
                models.Resume.id == resume_id
            ).first()
            
            if resume:
                # 更新简历内容
                resume.content = resume_text
                resume.parsed_data = analysis_result
                resume.processing_status = "completed"
                resume.processing_error = None
                resume.updated_at = datetime.utcnow()
                
                db.commit()
        except Exception as e:
            logger.error(f"更新简历内容失败: {str(e)}")
            raise

    async def _parse_word_file(self, file_path: str) -> str:
        """解析Word文件内容"""
        try:
            return await parser_service.parse_word(file_path)
        except Exception as e:
            logger.error(f"解析Word文件失败: {str(e)}")
            raise

    async def _parse_pdf_file(self, file_path: str) -> str:
        """解析PDF文件内容"""
        try:
            return await parser_service.parse_pdf(file_path)
        except Exception as e:
            logger.error(f"解析PDF文件失败: {str(e)}")
            raise

    async def _parse_text_file(self, file_path: str) -> str:
        """解析文本文件内容"""
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
            return content
        except UnicodeDecodeError:
            # 如果UTF-8解码失败，尝试其他编码
            encodings = ['gbk', 'gb2312', 'gb18030', 'latin1']
            for encoding in encodings:
                try:
                    async with aiofiles.open(file_path, 'r', encoding=encoding) as f:
                        content = await f.read()
                    return content
                except UnicodeDecodeError:
                    continue
            raise ValueError("无法识别文件编码")
        except Exception as e:
            logger.error(f"解析文本文件失败: {str(e)}")
            raise

    async def process_resume_by_id(self, resume_id: int) -> None:
        """根据简历ID处理简历内容
        
        Args:
            resume_id: 简历ID
        """
        # 创建新的数据库会话
        db = SessionLocal()
        try:
            # 1. 获取简历记录
            resume = db.query(models.Resume).filter(
                models.Resume.id == resume_id
            ).first()
            
            if not resume:
                logger.error(f"简历不存在: {resume_id}")
                return
                
            try:
                # 2. 解析文件
                resume_text = await parser_service.parse_resume(resume.file_path)
                
                # 3. 获取LLM配置
                llm_config = await llm_service.get_default_config(db)
                
                # 4. 分析简历内容
                analysis_result = await self._analyze_resume_with_llm(resume_text, llm_config)
                
                # 5. 更新简历记录
                resume.content = resume_text
                resume.parsed_data = analysis_result
                resume.processing_status = "completed"
                resume.processing_error = None
                resume.updated_at = datetime.utcnow()
                
                # 6. 更新基本字段
                resume_fields = self._extract_resume_fields(analysis_result)
                for field, value in resume_fields.items():
                    if hasattr(resume, field):
                        setattr(resume, field, value)
                
                # 7. 处理职位申请
                if resume.job_id:
                    job = job_service.get_job(db=db, job_id=resume.job_id)
                    if job:
                        if (job.tenant_id != resume.tenant_id and 
                                not resume.created_by.is_superuser):
                            raise ValueError("无权访问该职位")
                            
                        # 更新职位申请状态
                        job_application.status = "pending"
                        job_application.updated_at = datetime.utcnow()
                
                # 8. 提交更改
                db.commit()
                
                # 9. 记录日志
                logger.info(f"简历 {resume_id} 处理完成")
                
            except Exception as e:
                logger.error(f"处理简历失败: {str(e)}")
                resume.processing_status = "failed"
                resume.processing_error = str(e)
                db.commit()
                
        except Exception as e:
            logger.error(f"数据库操作失败: {str(e)}")
            db.rollback()
        finally:
            db.close()

    async def analyze_resume_with_ai(
        self,
        db: Session,
        resume_id: int,
        analysis_request: Dict,
        current_user: Any
    ) -> Dict:
        """
        使用AI对简历进行深度解读分析
        
        Args:
            db: 数据库会话
            resume_id: 简历ID
            analysis_request: 分析请求参数，包含job_requirements, dimensions等
            current_user: 当前用户
            
        Returns:
            包含分析结果的字典
        """
        # 1. 获取简历
        resume = self.get(db, id=resume_id)
        if not resume:
            raise HTTPException(status_code=404, detail="简历不存在")
        
        # 2. 验证租户权限
        if not current_user.is_superuser and resume.tenant_id != current_user.tenant_id:
            raise HTTPException(status_code=403, detail="无权限访问此简历")
        
        # 3. 检查简历内容
        if not resume.content:
            # 尝试重新解析简历
            try:
                from app.services.parser_service import parser_service
                resume_text = await parser_service.parse_resume(resume.file_path)
                resume.content = resume_text
                db.commit()
            except Exception as e:
                logger.error(f"解析简历失败: {str(e)}")
                raise HTTPException(status_code=500, detail="简历内容解析失败，请重试")
        
        # 4. 构建AI分析的输入数据
        resume_info = {
            "姓名": resume.name,
            "年龄": calculate_age(resume.birthdate) if resume.birthdate else "未知",
            "性别": resume.gender or "未知",
            "电话": resume.phone or "未知",
            "邮箱": resume.email or "未知",
            "当前公司": resume.current_company or "未知",
            "当前职位": resume.current_position or "未知",
            "工作年限": f"{resume.experience_years}年" if resume.experience_years is not None else "未知",
            "最高学历": resume.highest_education or "未知",
            "最高学历院校": resume.graduate_school or "未知",
            "最高学历专业": resume.major or "未知",
            "毕业时间": resume.graduation_date.strftime("%Y-%m-%d") if resume.graduation_date else "未知",
            "期望职位": resume.expected_position or "未知",
            "期望地点": resume.expected_location or "未知",
            "期望薪资": resume.expected_salary or "未知",
            "技能标签": ", ".join([skill.get("name", "") for skill in resume.skills]) if resume.skills and isinstance(resume.skills, list) else "未提供",
            "自我评价": resume.other_info or "未提供",
            "工作经历": work_history_to_text(resume.work_history if resume.work_history else []),
            "教育经历": education_info_to_text(resume.edu_experience if resume.edu_experience else []),
            "简历内容": resume.content,
        }
        
        # 5. 构建 LLM 提示
        job_requirements = analysis_request.get("job_requirements", "")
        dimensions = analysis_request.get("dimensions", [])
        
        prompt = f"""
        你是一位专业的招聘顾问，现在需要你对候选人简历进行深入分析，评估其与岗位的匹配程度。
        
        以下是候选人信息:
        ------------------------
        姓名: {resume_info['姓名']}
        年龄: {resume_info['年龄']}
        性别: {resume_info['性别']}
        当前公司: {resume_info['当前公司']}
        当前职位: {resume_info['当前职位']}
        工作年限: {resume_info['工作年限']}
        最高学历: {resume_info['最高学历']}
        毕业院校: {resume_info['最高学历院校']}
        专业: {resume_info['最高学历专业']}
        期望职位: {resume_info['期望职位']}
        期望地点: {resume_info['期望地点']}
        期望薪资: {resume_info['期望薪资']}
        技能标签: {resume_info['技能标签']}
        
        工作经历:
        {resume_info['工作经历']}
        
        教育经历:
        {resume_info['教育经历']}
        
        自我评价:
        {resume_info['自我评价']}
        
        简历内容:
        {resume_info['简历内容']}
        ------------------------
        
        职位要求:
        {job_requirements}
        
        请分析以下几个维度:
        {', '.join(dimensions)}
        """
        
        # 添加自定义问题
        if analysis_request.get("questions"):
            prompt += f"""
            
            请基于简历内容，回答以下问题:
            {analysis_request.get("questions")}
            """
        
        # 添加面试提示需求
        if analysis_request.get("include_interview_tips", True):
            prompt += """
            
            请提供针对此候选人的面试提示和建议问题。
            """
        
        prompt += """
        
        请以JSON格式返回分析结果，包含以下字段:
        1. summary: 候选人概要总结
        2. match_score: 职位匹配度分数(0-100)
        3. skill_analysis: 技能分析
        4. skills: 技能匹配列表，每项包含name(技能名称)和match(匹配度0-100)
        5. experience_analysis: 工作经验分析
        6. education_analysis: 教育背景分析
        7. career_analysis: 职业发展轨迹分析
        8. strengths: 优势列表(字符串数组)
        9. weaknesses: 劣势列表(字符串数组)
        10. interview_tips: 面试建议
        11. suggested_questions: 建议的面试问题列表(字符串数组)
        12. conclusion: 结论
        13. recommendation: 是否推荐("强烈推荐"/"推荐"/"谨慎推荐"/"不推荐")
        """
        
        # 6. 调用LLM服务
        try:
            llm_config = await llm_service.get_default_config(db)
            response = await llm_service.generate_completion(
                prompt=prompt,
                system_prompt=None,
                db=db,
                llm_config=llm_config
            )
            
            # 验证response格式
            if not isinstance(response, dict) or "content" not in response:
                logger.error(f"LLM响应格式错误: {response}")
                raise ValueError(f"LLM响应格式错误: {response}")
            
            # 7. 解析LLM响应
            result = parse_llm_response(response["content"])
            return result
            
        except Exception as e:
            logger.error(f"AI分析简历失败: {str(e)}")
            # 记录更多调试信息
            if 'response' in locals():
                logger.error(f"LLM响应: {response}")
            raise HTTPException(status_code=500, detail=f"AI分析失败: {str(e)}")

# 创建单例实例
resume_service = ResumeService()

# 辅助函数 - 从API层移到服务层
def calculate_age(birthdate):
    """计算年龄"""
    if not birthdate:
        return "未知"
    today = datetime.now()
    age = today.year - birthdate.year
    # 如果今年的生日还没到，年龄减1
    if today.month < birthdate.month or (today.month == birthdate.month and today.day < birthdate.day):
        age -= 1
    return f"{age}岁"


def work_history_to_text(work_history):
    """将工作经历转换为文本描述"""
    if not work_history:
        return "无工作经历记录"
    
    text = ""
    for i, work in enumerate(work_history):
        company = work.get('company', '未知公司')
        position = work.get('position', '未知职位')
        
        # 处理duration字段可能不存在的情况
        duration = work.get('duration', '')
        if not duration and ('start_date' in work or 'end_date' in work):
            start = work.get('start_date', '未知')
            end = work.get('end_date', '至今')
            duration = f"{start} - {end}"
        
        text += f"{i+1}. {company} | {position}"
        if duration:
            text += f" | {duration}"
        text += "\n"
        
        if work.get('description'):
            text += f"   描述: {work['description']}\n"
    return text


def education_info_to_text(education_info):
    """将教育经历转换为文本描述"""
    if not education_info:
        return "无教育经历记录"
    
    text = ""
    for i, edu in enumerate(education_info):
        school = edu.get('school', '未知学校')
        major = edu.get('major', '未知专业')
        degree = edu.get('degree', '未知学位')
        
        # 处理duration字段可能不存在的情况
        duration = edu.get('duration', '')
        if not duration and ('start_date' in edu or 'end_date' in edu):
            start = edu.get('start_date', '未知')
            end = edu.get('end_date', '至今')
            duration = f"{start} - {end}"
        
        text += f"{i+1}. {school} | {major} | {degree}"
        if duration:
            text += f" | {duration}"
        text += "\n"
    return text


def parse_llm_response(content):
    """解析LLM响应内容为结构化数据"""
    try:
        # 检查content是否已经是字典类型
        if isinstance(content, dict):
            result = content
        else:
            # 尝试将字符串解析为JSON
            import json
            try:
                result = json.loads(content)
            except json.JSONDecodeError:
                # 如果字符串不是合法的JSON，尝试从中提取JSON部分
                import re
                json_match = re.search(r'(\{.*\})', content, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group(1))
                else:
                    raise ValueError("无法从响应中提取JSON")
        
        # 确保所有必要字段都存在（使用驼峰命名法）
        required_fields = [
            "summary", "matchScore", "skillAnalysis", "experienceAnalysis", 
            "educationAnalysis", "careerAnalysis", "strengths", "weaknesses", 
            "conclusion", "recommendation", "interviewTips", "suggestedQuestions"
        ]
        
        for field in required_fields:
            if field not in result:
                result[field] = "未提供" if field not in ["strengths", "weaknesses", "skills", "suggestedQuestions"] else []
        
        # 强制转换matchScore为整数
        try:
            if isinstance(result["matchScore"], str):
                result["matchScore"] = int(result["matchScore"].replace("%", ""))
            elif isinstance(result["matchScore"], float):
                result["matchScore"] = int(result["matchScore"])
        except:
            result["matchScore"] = 0
            
        # 确保skills字段的格式正确
        if "skills" in result and result["skills"]:
            # 标准化skills字段
            standardized_skills = []
            for skill in result["skills"]:
                if isinstance(skill, dict):
                    skill_item = {
                        "name": skill.get("name", "未知技能"),
                        "match": skill.get("match", 0) 
                    }
                    standardized_skills.append(skill_item)
                elif isinstance(skill, str):
                    # 尝试解析文本格式的技能
                    parts = skill.split(":")
                    if len(parts) >= 2:
                        try:
                            match = int(parts[1].strip().replace("%", ""))
                        except:
                            match = 0
                        skill_item = {
                            "name": parts[0].strip(),
                            "match": match
                        }
                        standardized_skills.append(skill_item)
            
            result["skills"] = standardized_skills
            
        return result
        
    except Exception as e:
        # 如果解析失败，构造一个基本响应
        return {
            "summary": "无法解析AI响应内容",
            "matchScore": 0,
            "skillAnalysis": "分析失败",
            "skills": [],
            "experienceAnalysis": "分析失败",
            "educationAnalysis": "分析失败", 
            "careerAnalysis": "分析失败",
            "strengths": ["无法识别"],
            "weaknesses": ["无法识别"],
            "interviewTips": "无法提供",
            "suggestedQuestions": [],
            "conclusion": "由于技术原因，无法完成简历分析",
            "recommendation": "待定"
        }

# 只导出实例
__all__ = ["resume_service"] 