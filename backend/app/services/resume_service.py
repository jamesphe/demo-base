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

from app import models, crud
from app.core.config import settings
from app.schemas.resume import ResumeCreate, ResumeUpdate, SkillInfo, CertificateInfo
from .base import BaseService
from app.services import repository_service, llm_config_service
from app.services.parser_service import parser_service
from app.services.llm_service import llm_service

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
        # 设置JSON编码器
        self.json_encoder = DateTimeEncoder()

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

    async def process_resume_file(
        self,
        db: Session,
        file: UploadFile,
        repository_id: int,
        tenant_id: int,
        publisher_id: int = None,
        publisher_type: str = None,
        publisher_name: str = None
    ) -> models.Resume:
        """处理上传的简历文件"""
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

    async def _save_file(
        self, 
        file: UploadFile, 
        repository_id: int
    ) -> Dict[str, str]:
        """保存上传的文件"""
        if not self.validate_file_extension(file.filename):
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件类型: {file.filename}"
            )
            
        file_info = self._generate_file_info(file, repository_id)
        await self._write_file(file, file_info['file_path'])
        
        return file_info

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
        
        return {
            "content": resume_text,
            "parsed_data": analysis_result
        }

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
                # 转换为datetime对象再转回特定格式的字符串
                dt = datetime.strptime(date_str, "%Y-%m-%d")
                return dt.strftime("%Y-%m-%dT%H:%M:%S")
            except (ValueError, TypeError):
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
                if work.get("start_date"):
                    work["start_date"] = convert_to_datetime(work["start_date"])
                if work.get("end_date"):
                    work["end_date"] = convert_to_datetime(work["end_date"])
        
        # 处理教育经历日期
        edu_experience = parsed_data.get("edu_experience", [])
        if edu_experience:
            for edu in edu_experience:
                if edu.get("start_date"):
                    edu["start_date"] = convert_to_datetime(edu["start_date"])
                if edu.get("end_date"):
                    edu["end_date"] = convert_to_datetime(edu["end_date"])

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

    def get_resume(self, resume_id: int) -> Optional[models.Resume]:
        """获取简历"""
        return self.db.query(models.Resume).filter(
            models.Resume.id == resume_id
        ).first()

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
1. 所有日期必须使用YYYY-MM-DD格式
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
                processing_status="pending",
                matching_status='待匹配',
                resume_version=1,
                is_latest=True,
                source_channel=None,
                source_batch=None
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

# 创建服务实例
resume_service = ResumeService()

# 只导出实例
__all__ = ["resume_service"] 