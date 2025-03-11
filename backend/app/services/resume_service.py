from typing import List, Dict, Any
from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException
from datetime import datetime
import uuid
import os
import aiofiles

from app import models, crud
from app.core.config import settings
from app.schemas.resume_repository import ResumeRepositoryCreate
from app.schemas.resume import ResumeCreate, ResumeUpdate


class ResumeService:
    async def create_repository(
        self,
        db: Session,
        name: str,
        resume_type: str,
        description: str = None
    ) -> models.ResumeRepository:
        """创建新的简历库"""
        repo_in = ResumeRepositoryCreate(
            name=name,
            resume_type=resume_type,
            description=description
        )
        return crud.repository.create(db=db, obj_in=repo_in)

    async def save_file(
        self,
        file: UploadFile,
        repository_id: int
    ) -> Dict[str, str]:
        """保存上传的文件并返回文件信息"""
        # 验证文件扩展名
        ext = file.filename.split(".")[-1].lower()
        if ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件类型: {ext}"
            )
            
        # 生成唯一文件名和简历ID
        resume_id = str(uuid.uuid4())
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

    async def create_resume(
        self,
        db: Session,
        file_info: Dict[str, str],
        repository_id: int,
        resume_type: str
    ) -> models.Resume:
        """创建简历记录"""
        resume_in = ResumeCreate(
            resume_id=file_info["resume_id"],
            repository_id=repository_id,
            resume_type=resume_type,
            file_name=file_info["file_name"],
            file_path=file_info["file_path"],
            file_type=file_info["file_type"],
            processing_status="pending",
            created_at=datetime.utcnow()
        )
        return crud.resume.create(db=db, obj_in=resume_in)

    async def process_resumes_in_chunks(
        self,
        repository_id: int,
        resume_infos: List[Dict[str, Any]],
        db: Session
    ) -> None:
        """批量处理简历"""
        for resume_info in resume_infos:
            try:
                await self.process_single_resume(resume_info, db)
            except Exception as e:
                # 记录错误但继续处理其他简历
                await self.update_resume_status(
                    resume_info["id"],
                    "failed",
                    db,
                    error=str(e)
                )

    async def process_single_resume(
        self,
        resume_info: Dict[str, Any],
        db: Session
    ) -> None:
        """处理单个简历"""
        resume_id = resume_info["id"]
        try:
            # 更新处理开始状态
            await self.update_resume_status(
                resume_id,
                "processing",
                db,
                started_at=datetime.utcnow()
            )

            # TODO: 实现简历解析逻辑
            parsed_data = await self.parse_resume(resume_info["file_path"])
            
            # 更新简历信息
            resume_update = ResumeUpdate(
                processing_status="completed",
                processing_completed_at=datetime.utcnow(),
                parsed_data=parsed_data,
                **self.extract_resume_fields(parsed_data)
            )
            
            await self.update_resume(resume_id, resume_update, db)
            
        except Exception as e:
            await self.update_resume_status(
                resume_id,
                "failed",
                db,
                error=str(e)
            )
            raise

    async def parse_resume(self, file_path: str) -> Dict[str, Any]:
        """解析简历文件"""
        # TODO: 实现实际的简历解析逻辑
        return {
            "name": "示例姓名",
            "email": "example@email.com",
            "phone": "13800138000",
            "education": {
                "degree": "本科",
                "school": "示例大学",
                "major": "计算机科学"
            },
            "skills": ["Python", "FastAPI", "SQL"],
            "work_history": []
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
            "skills": parsed_data.get("skills"),
            "work_history": parsed_data.get("work_history")
        }

    async def update_resume_status(
        self,
        resume_id: int,
        status: str,
        db: Session,
        error: str = None,
        started_at: datetime = None
    ) -> None:
        """更新简历状态"""
        update_data = {
            "processing_status": status
        }
        
        if error:
            update_data["processing_error"] = error
        if started_at:
            update_data["processing_started_at"] = started_at
        if status == "completed":
            update_data["processing_completed_at"] = datetime.utcnow()
            
        resume = crud.resume.get(db, resume_id)
        if resume:
            crud.resume.update(db, db_obj=resume, obj_in=update_data)

    async def update_resume(
        self,
        resume_id: int,
        resume_update: ResumeUpdate,
        db: Session
    ) -> models.Resume:
        """更新简历信息"""
        resume = crud.resume.get(db, resume_id)
        if not resume:
            raise HTTPException(status_code=404, detail="简历不存在")
        return crud.resume.update(db, db_obj=resume, obj_in=resume_update) 