from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException
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
from fastapi import BackgroundTasks

from app import models, crud
from app.core.config import settings
from app.schemas.resume_repository import ResumeRepositoryCreate
from app.schemas.resume import ResumeCreate, ResumeUpdate
from .base import BaseService
from app.services import repository_service, llm_config_service
from app.services.parser_service import parser_service
from app.services.llm_service import llm_service
from app.services.talent_service import TalentService
from app.schemas.talent import TalentCreate

# 设置日志
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

class ResumeService(BaseService[models.Resume, ResumeCreate, ResumeUpdate]):
    """简历服务"""
    
    def __init__(self):
        super().__init__(models.Resume)

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
        repository = crud.repository.get_by_name(db, name=name)
        if not repository:
            repository = await repository_service.create_repository(
                db,
                name=name,
                resume_type=resume_type,
                description=description,
                tenant_id=tenant_id
            )
        return repository

    async def save_file(
        self,
        file: UploadFile,
        repository_id: int
    ) -> Dict[str, str]:
        """保存上传的文件并返回文件信息"""
        # 验证文件扩展名
        if not self.validate_file_extension(file.filename):
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件类型: {file.filename}"
            )
            
        # 生成唯一文件名和简历ID
        resume_id = str(uuid.uuid4())
        ext = file.filename.split(".")[-1].lower()
        unique_filename = f"{resume_id}.{ext}"
        repository_path = os.path.join(settings.UPLOAD_DIR, str(repository_id))
        
        # 确保目录存在
        os.makedirs(repository_path, exist_ok=True)
        
        file_path = os.path.join(repository_path, unique_filename)
        
        # 异步保存文件
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)
            
        return {
            "resume_id": resume_id,
            "file_name": file.filename,
            "file_path": file_path,
            "file_type": ext
        }

    async def process_resume_file(
        self,
        db: Session,
        file: UploadFile,
        repository_id: int,
        tenant_id: Optional[int] = None
    ) -> models.Resume:
        """处理简历文件"""
        file_info = None
        try:
            logger.debug("=== Processing Resume File ===")
            logger.debug(f"File name: {file.filename}")
            logger.debug(f"Content type: {file.content_type}")
            logger.debug(f"Tenant ID: {tenant_id}")

            # 保存文件
            file_info = await self.save_file(file, repository_id)
            logger.debug(f"File saved: {pformat(file_info)}")

            # 解析简历文本 - 使用已保存的文件路径
            resume_text = await parser_service.parse_resume(file_info["file_path"])
            logger.debug(f"Parsed resume text (first 500 chars): {resume_text[:500]}...")

            # 获取 LLM 配置
            llm_config = await llm_service.get_default_config(db)
            logger.debug(f"LLM config: {pformat(llm_config.__dict__)}")

            # 生成简历分析提示词
            system_prompt = self._get_system_prompt()
            prompt = self._get_analysis_prompt(resume_text)
            logger.debug(f"System prompt: {system_prompt}")
            logger.debug(f"Analysis prompt: {prompt}")

            # 调用 LLM 分析简历
            try:
                result = await llm_service.generate_completion(
                    prompt=prompt,
                    llm_config=llm_config,
                    system_prompt=system_prompt
                )
                logger.debug(f"LLM analysis result: {pformat(result)}")
            except Exception as e:
                logger.error("LLM analysis failed", exc_info=True)
                raise ValueError(f"简历分析失败: {str(e)}")

            # 解析 LLM 返回的 JSON
            try:
                analysis_result = json.loads(result["content"])
                logger.debug(f"Parsed analysis result: {pformat(analysis_result)}")
            except json.JSONDecodeError as e:
                logger.error("Failed to parse LLM response as JSON", exc_info=True)
                logger.error(f"Raw response: {result['content']}")
                raise ValueError("简历分析结果格式错误")

            # 创建人才记录
            try:
                talent_data = {
                    "tenant_id": tenant_id,
                    "data_source": "个人用户",
                    **analysis_result  # 展开分析结果
                }
                logger.debug(f"Talent create data: {pformat(talent_data)}")
                
                talent_create = TalentCreate(**talent_data)
                logger.debug(f"Talent create model: {pformat(talent_create.__dict__)}")
                
                # 创建人才记录
                talent_service = TalentService(db)
                talent = talent_service.create_talent(talent_create)
                logger.debug(f"Talent created: {talent.talent_id}")
                
                # 创建简历记录
                resume = await self.create_resume(
                    db,
                    file_path=file_info["file_path"],
                    repository_id=repository_id,
                    original_filename=file.filename,
                    tenant_id=tenant_id
                )
                
                # 更新简历信息，关联人才ID
                resume = self.update(
                    db=db,
                    db_obj=resume,
                    obj_in=ResumeUpdate(
                        content=resume_text,
                        parsed_data=talent_data,
                        talent_id=talent.talent_id,
                        processing_status="completed"
                    )
                )
                
                return {
                    "talent": talent,
                    "resume": resume
                }
                
            except ValidationError as e:
                logger.error("Talent data validation failed", exc_info=True)
                logger.error(f"Validation errors: {e.errors()}")
                raise ValueError(f"人才数据验证失败: {str(e)}")

        except HTTPException as e:
            # 清理文件
            if file_info and "file_path" in file_info:
                self.delete_file(file_info["file_path"])
            raise  # 重新抛出 HTTP 异常
            
        except Exception as e:
            # 清理文件
            if file_info and "file_path" in file_info:
                self.delete_file(file_info["file_path"])
            raise HTTPException(
                status_code=500,
                detail=f"简历处理失败: {str(e)}"
            )

    async def _parse_resume_file(self, file: UploadFile) -> str:
        """解析简历文件内容"""
        try:
            logger.debug(f"Parsing resume file: {file.filename}")
            
            # 创建临时文件
            temp_dir = os.path.join(settings.UPLOAD_DIR, "temp")
            os.makedirs(temp_dir, exist_ok=True)
            temp_path = os.path.join(temp_dir, file.filename)
            
            # 先读取文件内容
            content = await file.read()
            # 重置文件指针，这样后续还能读取
            await file.seek(0)
            
            # 保存上传的文件到临时目录
            try:
                async with aiofiles.open(temp_path, 'wb') as out_file:
                    await out_file.write(content)
                logger.debug(f"Saved temp file: {temp_path}")
                
                # 使用 parser_service 解析文件
                resume_text = await parser_service.parse_resume(temp_path)
                logger.debug("Resume parsing successful")
                
                return resume_text
                
            finally:
                # 清理临时文件
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                    logger.debug(f"Cleaned up temp file: {temp_path}")
                    
        except Exception as e:
            logger.error("Resume parsing failed", exc_info=True)
            raise ValueError(f"简历解析失败: {str(e)}")

    def _get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """你是一个专业的简历分析助手。请从简历文本中提取关键信息，并以JSON格式返回。
        确保提取以下字段：
        - name: 姓名
        - gender: 性别 (M/F)
        - birth_date: 出生日期 (YYYY-MM-DD)
        - phone: 电话
        - email: 邮箱
        - address: 地址
        - profile_summary: 个人简介
        - primary_job_type: 主要职业类型
        - job_location_preference: 期望工作地点
        - expected_salary: 期望薪资
        """

    def _get_analysis_prompt(self, resume_text: str) -> str:
        """生成分析提示词"""
        return f"""请分析以下简历文本，提取关键信息并以JSON格式返回：

简历文本：
{resume_text}

请确保返回的JSON包含所有必需字段，对于无法确定的字段请返回null。
"""

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

    def extract_resume_fields(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """从解析数据中提取简历字段"""
        return {
            "name": parsed_data.get("name"),
            "email": parsed_data.get("email"),
            "phone": parsed_data.get("phone"),
            "highest_education": parsed_data.get("education", {}).get("degree"),
            "graduate_school": parsed_data.get("education", {}).get("school"),
            "major": parsed_data.get("education", {}).get("major"),
            "skills": parsed_data.get("skills")
        }

    def delete_file(self, file_path: str) -> None:
        """删除简历文件"""
        if os.path.exists(file_path):
            os.remove(file_path)

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
        tenant_id: Optional[int] = None
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
                processing_status="pending"
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

    async def update_resume_status(
        self,
        db: Session,
        *,
        resume_id: str,
        status: str,
        error: Optional[str] = None
    ) -> models.Resume:
        """更新简历处理状态"""
        resume = self.get_by_resume_id(db, resume_id=resume_id)
        if not resume:
            raise HTTPException(status_code=404, detail="简历不存在")
        
        update_data = {
            "processing_status": status,
            "processing_error": error,
            "processing_completed_at": datetime.utcnow() if status == "completed" else None
        }
        
        return self.update(
            db=db,
            db_obj=resume,
            obj_in=ResumeUpdate(**update_data)
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
            resume_fields = self.extract_resume_fields(parsed_data)
            
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
            keyword_filter = or_(
                models.Resume.name.ilike(f"%{keyword}%"),
                models.Resume.email.ilike(f"%{keyword}%"),
                models.Resume.phone.ilike(f"%{keyword}%"),
                models.Resume.content.ilike(f"%{keyword}%"),
                models.Resume.skills.ilike(f"%{keyword}%"),
                models.Resume.major.ilike(f"%{keyword}%"),
                models.Resume.graduate_school.ilike(f"%{keyword}%")
            )
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
            
        target_repo = crud.repository.get(db, id=target_repository_id)
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
            self.delete_file(resume.file_path)
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
                source_file = resume.file_path
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
                self.delete_file(resume.file_path)
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


# 创建服务实例
resume_service = ResumeService()

# 只导出实例
__all__ = ["resume_service"] 