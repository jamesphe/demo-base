import os
import shutil
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session
from app import crud, models, schemas
from app.api import deps
from app.core.config import settings
from datetime import datetime
import uuid
import aiofiles
from app.services.resume_service import ResumeService

router = APIRouter()
resume_service = ResumeService()

def validate_file_extension(filename: str) -> bool:
    allowed_extensions = settings.ALLOWED_EXTENSIONS
    return filename.split(".")[-1].lower() in allowed_extensions

@router.post("/upload")
async def upload_files(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    repository_name: str = Form(...),
    resume_type: str = Form(...),
    description: str = Form(None),
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """批量上传简历文件到指定简历库"""
    try:
        # 1. 创建简历库
        repository = await resume_service.create_repository(
            db, 
            repository_name,
            resume_type, 
            description
        )
        
        # 2. 异步保存文件
        saved_files = []
        for file in files:
            file_info = await resume_service.save_file(
                file, 
                repository.id
            )
            saved_files.append(file_info)
        
        # 3. 创建简历记录
        resumes = []
        for file_info in saved_files:
            resume = await resume_service.create_resume(
                db,
                file_info,
                repository.id,
                resume_type
            )
            resumes.append(resume)
        
        db.commit()

        # 4. 添加后台处理任务
        background_tasks.add_task(
            resume_service.process_resumes_in_chunks,
            repository.id,
            [{"id": r.id, "file_path": r.file_path} for r in resumes],
            db
        )

        return {
            "code": 200,
            "message": "上传成功", 
            "repository_id": repository.id,
            "files": [{"name": r.file_name, "id": r.id} for r in resumes]
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{resume_id}", response_model=schemas.Resume)
def get_resume(
    *,
    resume_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    获取简历信息
    """
    resume = crud.resume.get(db=db, id=resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="简历不存在")
    return resume

@router.get("/candidate/{candidate_id}", response_model=list[schemas.Resume])
def get_candidate_resumes(
    *,
    candidate_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    获取候选人的所有简历
    """
    resumes = crud.resume.get_by_candidate_id(db=db, candidate_id=candidate_id)
    return resumes

@router.get("/parse")
async def parse_resume(
    *,
    file_url: str,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    解析简历内容
    """
    # TODO: 实现简历解析逻辑
    return {
        "parsed_data": {
            "name": "示例姓名",
            "email": "example@email.com",
            "skills": ["Python", "FastAPI"]
        }
    } 