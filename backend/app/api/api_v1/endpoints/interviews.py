from typing import Any, List, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime
import logging
import json
import sys

from app import crud, models, schemas
from app.api import deps
from app.schemas.interview import InterviewType
from app.services.interview_service import interview_service

router = APIRouter()


@router.get("", response_model=schemas.InterviewListResponse)
def read_interviews(
    db: Session = Depends(deps.get_db),
    page: int = Query(1, ge=1, description="页码"),
    per_page: int = Query(10, ge=1, le=100, description="每页数量"),
    interviewer_id: Optional[int] = Query(None, description="面试官ID"),
    type: Optional[str] = Query(None, description="面试类型"),
    status: Optional[str] = Query(None, description="面试状态"),
    candidate_name: Optional[str] = Query(None, description="候选人姓名"),
    start_date: Optional[datetime] = Query(None, description="开始日期"),
    end_date: Optional[datetime] = Query(None, description="结束日期"),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """获取面试列表"""
    skip = (page - 1) * per_page
    
    # 检查用户角色
    admin_roles = ["admin", "hr", "hr_manager", "tenant_admin"]
    is_admin_or_manager = (
        current_user.is_superuser 
        or any(role in admin_roles for role in current_user.get_roles())
    )
    
    # 面试官只能查看自己参与的面试
    if not is_admin_or_manager:
        interviewer_id = current_user.id
        
    print(f"调试: 收到请求参数 - interviewer_id={interviewer_id}, type={type}, status={status}")
    
    if interviewer_id or type or status or candidate_name or start_date or end_date:
        # 使用search_interviews方法进行高级搜索
        interviews = interview_service.search_interviews(
            db,
            tenant_id=None if current_user.is_superuser else current_user.tenant_id,
            keyword=candidate_name,
            interviewer_id=interviewer_id,
            status=status,
            interview_type=type,  # 将type参数传递给interview_type
            start_date=start_date,
            end_date=end_date,
            skip=skip,
            limit=per_page
        )
        # 总数统计需要单独查询
        if current_user.is_superuser:
            total = crud.interview.count(db)
        else:
            total = crud.interview.count_by_tenant(
                db, 
                tenant_id=current_user.tenant_id
            )
    else:
        # 使用传统查询方式
        if current_user.is_superuser:
            interviews = crud.interview.get_multi_with_details(db, skip=skip, limit=per_page)
            total = crud.interview.count(db)
        else:
            # 面试官只能看到自己的面试
            if not is_admin_or_manager:
                interviews = crud.interview.get_by_interviewer(
                    db, 
                    interviewer_id=current_user.id,
                    skip=skip,
                    limit=per_page
                )
                total = crud.interview.count_by_interviewer(
                    db, 
                    interviewer_id=current_user.id
                )
            else:
                # 租户管理员看到所有本租户的面试
                interviews = crud.interview.get_multi_by_tenant_with_details(
                    db,
                    tenant_id=current_user.tenant_id,
                    skip=skip,
                    limit=per_page
                )
                total = crud.interview.count_by_tenant(
                    db, 
                    tenant_id=current_user.tenant_id
                )
    
    total_pages = (total + per_page - 1) // per_page
    
    # 序列化处理，将SQLAlchemy对象转换为可以JSON序列化的字典
    serialized_interviews = []
    for interview in interviews:
        # 创建基础数据
        interview_dict = {
            "id": interview.id,
            "resume_id": interview.resume_id,
            "job_id": interview.job_id,
            "status": interview.status,
            "schedule_time": interview.schedule_time,
            "feedback": interview.feedback,
            "location": interview.location,
            "interview_type": interview.interview_type,
            "duration": interview.duration,
            "notes": interview.notes,
            "created_at": interview.created_at,
            "updated_at": interview.updated_at,
            "resume_title": None,  # 初始化resume_title
            "job_title": None,     # 初始化job_title
            "interviewer_names": []  # 初始化interviewer_names为空列表
        }
        
        # 处理Resume对象
        if hasattr(interview, "resume") and interview.resume:
            interview_dict["resume"] = {
                "id": interview.resume.id,
                "name": interview.resume.name,
                "phone": interview.resume.phone,
                "email": interview.resume.email,
                "gender": interview.resume.gender,
                "highest_education": interview.resume.highest_education,
                "major": interview.resume.major
            }
            # 更新resume_title
            interview_dict["resume_title"] = interview.resume.name
        
        # 处理Job对象
        if hasattr(interview, "job") and interview.job:
            interview_dict["job"] = {
                "id": interview.job.id,
                "title": interview.job.title,
                "department": getattr(interview.job, "department", None)
            }
            # 更新job_title
            interview_dict["job_title"] = interview.job.title
        
        # 处理面试官对象
        if hasattr(interview, "interviewers") and interview.interviewers:
            interview_dict["interviewers"] = []
            interview_dict["interviewer_names"] = []  # 面试官姓名列表
            for interviewer in interview.interviewers:
                interview_dict["interviewers"].append({
                    "id": interviewer.id,
                    "username": interviewer.username,
                    "email": interviewer.email,
                    "avatar": getattr(interviewer, "avatar", None)
                })
                # 添加面试官姓名到列表
                interview_dict["interviewer_names"].append(
                    interviewer.username
                )
        
        serialized_interviews.append(interview_dict)
    
    return {
        "data": serialized_interviews,
        "meta": {
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages
        }
    }


@router.post(
    "",
    response_model=schemas.Interview,
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["interview_create"]
            )
        )
    ]
)
def create_interview(
    *,
    db: Session = Depends(deps.get_db),
    interview_in: schemas.InterviewCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """创建新面试"""
    # 配置日志
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    
    # 添加控制台处理器
    if not logger.handlers:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
            '%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # 记录原始请求数据
    try:
        request_data = interview_in.dict()
        logger.debug(f"请求数据: {json.dumps(request_data, default=str)}")
    except Exception as e:
        logger.error(f"解析请求数据时出错: {str(e)}")
        logger.debug(f"直接打印请求对象: {interview_in}")
    
    # 1. 处理职位ID
    try:
        job_id = interview_in.job_id
        logger.debug(f"职位ID: {job_id}")
        
        if not job_id:
            logger.error("缺少必须的职位ID")
            raise HTTPException(status_code=400, detail="职位ID不能为空")
        
        # 检查职位是否存在
        job = db.query(models.Job).filter(models.Job.id == job_id).first()
        if not job:
            logger.error(f"职位ID {job_id} 不存在")
            raise HTTPException(status_code=404, detail="职位不存在")
    except Exception as e:
        logger.error(f"处理职位ID时出错: {str(e)}")
        raise HTTPException(status_code=400, detail=f"职位ID处理错误: {str(e)}")
    
    # 2. 处理简历ID
    resume_id = None
    try:
        # 如果传入了candidates数组，则使用第一个候选人
        candidates = getattr(interview_in, 'candidates', None)
        logger.debug(f"候选人数组: {candidates}")
        
        if candidates and len(candidates) > 0:
            candidate_info = candidates[0]
            logger.debug(f"候选人信息: {candidate_info}")
            
            # 尝试从candidateInfo中获取resumeId
            if isinstance(candidate_info, dict) and "resumeId" in candidate_info:
                resume_id = candidate_info.get("resumeId")
                logger.debug(f"从candidate_info中获取到resumeId: {resume_id}")
            
            # 如果没有resumeId但有applicationId
            if not resume_id and isinstance(candidate_info, dict) and "applicationId" in candidate_info:
                application_id = candidate_info.get("applicationId")
                logger.debug(f"使用applicationId查找: {application_id}")
                
                if application_id:
                    try:
                        # 如果提供了applicationId，查找对应的简历ID
                        logger.debug(f"查询JobApplication表, id={application_id}")
                        job_application = db.query(models.JobApplication).filter(
                            models.JobApplication.id == application_id
                        ).first()
                        
                        if job_application:
                            logger.debug(f"找到JobApplication记录: {job_application.id}")
                            resume_id = job_application.resume_id
                            logger.debug(f"简历ID: {resume_id}, 原job_id: {job_id}")
                            
                            # 如果没有指定job_id，则使用申请的job_id
                            if not job_id:
                                job_id = job_application.job_id
                                logger.debug(f"使用申请中的job_id: {job_id}")
                        else:
                            logger.error(f"未找到applicationId={application_id}的申请记录")
                    except Exception as e:
                        logger.error(f"查询JobApplication记录时出错: {str(e)}")
                        raise HTTPException(
                            status_code=400, 
                            detail=f"查询申请记录失败: {str(e)}"
                        )
        
        # 如果candidates处理失败，尝试从candidate_id获取resumeId
        if not resume_id:
            candidate_id = getattr(interview_in, 'candidate_id', None)
            logger.debug(f"使用candidate_id查找: {candidate_id}")
            
            if candidate_id:
                candidate = db.query(models.Candidate).filter(
                    models.Candidate.id == candidate_id
                ).first()
                
                if not candidate:
                    logger.error(f"候选人ID {candidate_id} 不存在")
                    raise HTTPException(status_code=404, detail="候选人不存在")
                
                resume_id = candidate.resume_id
                logger.debug(f"从candidate获取到resumeId: {resume_id}")
    except Exception as e:
        logger.error(f"处理候选人/简历ID时出错: {str(e)}")
        raise HTTPException(status_code=400, detail=f"简历ID处理错误: {str(e)}")
    
    # 验证resumeId是否存在
    if not resume_id:
        logger.error("未找到有效的简历ID")
        raise HTTPException(status_code=400, detail="未找到有效的简历ID")
    
    # 验证简历是否存在
    try:
        resume = db.query(models.Resume).filter(models.Resume.id == resume_id).first()
        if not resume:
            logger.error(f"简历ID {resume_id} 不存在")
            raise HTTPException(status_code=404, detail="简历不存在")
    except Exception as e:
        logger.error(f"检查简历ID时出错: {str(e)}")
        raise HTTPException(status_code=400, detail=f"简历检查错误: {str(e)}")
    
    # 3. 处理面试官ID - 修改为处理多个面试官
    try:
        # 获取面试官ID列表，优先使用interviewer_ids字段
        interviewer_ids = []
        if hasattr(interview_in, 'interviewer_ids') and interview_in.interviewer_ids:
            interviewer_ids = interview_in.interviewer_ids
        # 如果没有interviewer_ids，尝试使用interviewers字段
        elif hasattr(interview_in, 'interviewers') and interview_in.interviewers:
            interviewer_ids = interview_in.interviewers
        # 兼容旧版本，支持单个interviewer_id
        elif hasattr(interview_in, 'interviewer_id') and interview_in.interviewer_id:
            interviewer_ids = [interview_in.interviewer_id]
        
        logger.debug(f"面试官ID列表: {interviewer_ids}")
        
        if not interviewer_ids:
            logger.error("未提供面试官ID")
            raise HTTPException(status_code=400, detail="未提供面试官ID")
        
        # 验证所有面试官是否存在
        interviewers = []
        for interviewer_id in interviewer_ids:
            interviewer = db.query(models.User).filter(models.User.id == interviewer_id).first()
            if not interviewer:
                logger.error(f"面试官ID {interviewer_id} 不存在")
                raise HTTPException(status_code=404, detail=f"面试官ID {interviewer_id} 不存在")
            interviewers.append(interviewer)
            
    except Exception as e:
        logger.error(f"处理面试官ID时出错: {str(e)}")
        raise HTTPException(status_code=400, detail=f"面试官处理错误: {str(e)}")
    
    # 4. 检查租户权限
    try:
        if not current_user.is_superuser:
            # 检查是否有权限访问该简历
            if resume.tenant_id != current_user.tenant_id:
                logger.error(
                    f"权限不足: 用户租户={current_user.tenant_id}, 简历租户={resume.tenant_id}"
                )
                raise HTTPException(status_code=403, detail="无权为该候选人安排面试")
            
            # 检查是否有权限指定这些面试官
            for interviewer in interviewers:
                if interviewer.tenant_id != current_user.tenant_id:
                    logger.error(
                        f"权限不足: 用户租户={current_user.tenant_id}, 面试官租户={interviewer.tenant_id}"
                    )
                    raise HTTPException(status_code=403, detail="无权指定该面试官")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"检查租户权限时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"权限检查错误: {str(e)}")
    
    # 5. 处理面试时间
    try:
        schedule_time = None
        time_str = getattr(interview_in, 'time', None)
        
        if time_str:
            try:
                schedule_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
                logger.debug(f"解析time字段为: {schedule_time}")
            except ValueError as e:
                logger.error(f"时间格式解析错误: {str(e)}")
                raise HTTPException(status_code=400, detail="面试时间格式不正确，应为yyyy-MM-dd HH:mm:ss")
        else:
            schedule_time = getattr(interview_in, 'schedule_time', None)
            logger.debug(f"使用schedule_time字段: {schedule_time}")
        
        if not schedule_time:
            logger.error("面试时间不能为空")
            raise HTTPException(status_code=400, detail="面试时间不能为空")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"处理面试时间时出错: {str(e)}")
        raise HTTPException(status_code=400, detail=f"面试时间处理错误: {str(e)}")
    
    # 6. 处理面试类型
    try:
        interview_type = None
        type_str = getattr(interview_in, 'type', None)
        
        logger.debug(f"面试类型字符串: {type_str}")
        
        if type_str:
            if type_str == "first":
                interview_type = InterviewType.FIRST
            elif type_str == "second":
                interview_type = InterviewType.SECOND
            elif type_str == "final":
                interview_type = InterviewType.FINAL
            else:
                logger.warning(f"未知的面试类型: {type_str}，使用默认值")
                interview_type = InterviewType.FIRST
        else:
            interview_type = getattr(interview_in, 'interview_type', None) or InterviewType.FIRST
        
        logger.debug(f"最终使用的面试类型: {interview_type}")
    except Exception as e:
        logger.error(f"处理面试类型时出错: {str(e)}")
        raise HTTPException(status_code=400, detail=f"面试类型处理错误: {str(e)}")
    
    # 7. 处理其他参数
    try:
        duration = getattr(interview_in, 'duration', 60) or 60
        location = getattr(interview_in, 'location', None)
        notes = getattr(interview_in, 'notes', None)
        
        logger.debug(
            f"其他参数: duration={duration}, location={location}, notes={notes}"
        )
    except Exception as e:
        logger.error(f"处理其他参数时出错: {str(e)}")
        raise HTTPException(status_code=400, detail=f"参数处理错误: {str(e)}")
    
    # 8. 通过服务层创建面试
    try:
        logger.info(
            f"创建面试: resume_id={resume_id}, job_id={job_id}, "
            f"interviewer_ids={interviewer_ids}, time={schedule_time}"
        )
        
        # 使用更新后的schedule_interview方法支持多个面试官
        interview = interview_service.schedule_interview(
            db=db,
            resume_id=resume_id,
            job_id=job_id,
            interviewer_ids=interviewer_ids,  # 传递面试官ID列表
            interview_time=schedule_time,
            duration=duration,
            location=location,
            interview_type=interview_type,
            notes=notes,
            current_user=current_user
        )
        
        logger.info(f"面试创建成功: {interview.id}")
        return interview
    except ValueError as e:
        error_msg = str(e)
        if "面试官在该时间段已有其他面试安排" in error_msg:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "面试时间冲突",
                    "details": "面试官在该时间段已有其他面试安排，请选择其他时间"
                }
            )
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"创建面试失败: {str(e)}")
        raise HTTPException(status_code=400, detail=f"创建面试失败: {str(e)}")


@router.get(
    "/candidate/{candidate_id}",
    response_model=List[schemas.InterviewWithDetails],
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["interview_read"]
            )
        )
    ]
)
def read_candidate_interviews(
    candidate_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """获取候选人的面试记录"""
    # 验证候选人是否存在
    candidate = crud.candidate.get(db, id=candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="候选人不存在")
    
    # 检查租户权限
    if not current_user.is_superuser and candidate.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="无权访问该候选人的面试记录")
    
    interviews = crud.interview.get_by_candidate(db, candidate_id=candidate_id)
    return interviews


@router.get(
    "/interviewer/{interviewer_id}",
    response_model=List[schemas.InterviewWithDetails],
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["interview_read"]
            )
        )
    ]
)
def read_interviewer_interviews(
    interviewer_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """获取面试官的面试安排"""
    # 验证面试官是否存在
    interviewer = crud.user.get(db, id=interviewer_id)
    if not interviewer:
        raise HTTPException(status_code=404, detail="面试官不存在")
    
    # 检查租户权限
    if not current_user.is_superuser and interviewer.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="无权访问该面试官的面试安排")
    
    interviews = crud.interview.get_by_interviewer(db, interviewer_id=interviewer_id)
    return interviews


@router.put(
    "/{interview_id}",
    response_model=schemas.Interview,
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["interview_update"]
            )
        )
    ]
)
def update_interview(
    *,
    db: Session = Depends(deps.get_db),
    interview_id: int,
    interview_in: schemas.InterviewUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """更新面试信息"""
    interview = crud.interview.get(db=db, id=interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="面试不存在")
    
    # 检查租户权限
    resume = db.query(models.Resume).filter(models.Resume.id == interview.resume_id).first()
    if not current_user.is_superuser and resume and resume.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="无权更新该面试信息")
    
    # 获取面试官ID列表，如果提供了
    interviewer_ids = None
    if hasattr(interview_in, 'interviewer_ids') and interview_in.interviewer_ids is not None:
        interviewer_ids = interview_in.interviewer_ids
    elif hasattr(interview_in, 'interviewers') and getattr(interview_in, 'interviewers') is not None:
        interviewer_ids = interview_in.interviewers
    
    # 使用支持多面试官的更新方法
    if hasattr(crud.interview, 'update_with_interviewers') and interviewer_ids is not None:
        interview = crud.interview.update_with_interviewers(
            db=db,
            db_obj=interview,
            obj_in=interview_in,
            interviewer_ids=interviewer_ids
        )
    else:
        interview = crud.interview.update(
            db=db,
            db_obj=interview,
            obj_in=interview_in
        )
    return interview


@router.delete(
    "/{interview_id}",
    response_model=schemas.Interview,
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["interview_delete"]
            )
        )
    ]
)
def delete_interview(
    *,
    db: Session = Depends(deps.get_db),
    interview_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """删除面试"""
    interview = crud.interview.get(db=db, id=interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="面试不存在")
    
    # 检查租户权限
    resume = db.query(models.Resume).filter(models.Resume.id == interview.resume_id).first()
    if not current_user.is_superuser and resume and resume.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="无权删除该面试")
    
    interview = crud.interview.remove(db=db, id=interview_id)
    return interview


@router.get("/interviewers", response_model=schemas.UserListResponse)
def read_interviewers(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    page: int = Query(1, ge=1, description="页码"),
    per_page: int = Query(10, ge=1, le=100, description="每页数量"),
) -> Any:
    """获取面试官列表"""
    interviewers = interview_service.get_interviewers(
        db, tenant_id=current_user.tenant_id, page=page, per_page=per_page
    )
    return interviewers


@router.put("/{interview_id}/interviewers/{interviewer_id}/preparation-notes")
async def update_interviewer_preparation_notes(
    *,
    db: Session = Depends(deps.get_db),
    interview_id: int,
    interviewer_id: int,
    data: Dict[str, Any],
    current_user: models.User = Depends(deps.get_current_user)
) -> Any:
    """更新面试官准备材料"""
    # 检查面试是否存在
    interview = crud.interview.get(db=db, id=interview_id)
    if not interview:
        raise HTTPException(
            status_code=404,
            detail="面试不存在"
        )
    
    # 检查当前用户是否有权限
    if not crud.user.is_superuser(current_user) and current_user.id != interviewer_id:
        raise HTTPException(
            status_code=403, 
            detail="没有权限更新其他面试官的准备材料"
        )
    
    # 检查该面试官是否参与了这次面试
    interviewer_ids = [interviewer.id for interviewer in interview.interviewers]
    if interviewer_id not in interviewer_ids:
        raise HTTPException(
            status_code=400,
            detail="该面试官未参与此次面试"
        )
    
    # 更新面试准备材料
    preparation_notes = data.get("preparation_notes", "")
    db.query(models.interview_interviewers).filter(
        models.interview_interviewers.c.interview_id == interview_id,
        models.interview_interviewers.c.interviewer_id == interviewer_id
    ).update({"preparation_notes": preparation_notes})
    db.commit()
    
    return {"status": "success", "message": "面试准备材料已更新"}


@router.post("/{interview_id}/interviewers/{interviewer_id}/preparation-notes/generate")
async def generate_interviewer_preparation_notes(
    *,
    db: Session = Depends(deps.get_db),
    interview_id: int,
    interviewer_id: int,
    data: Dict[str, Any],
    current_user: models.User = Depends(deps.get_current_user)
) -> Any:
    """AI生成面试官准备材料"""
    # 检查面试是否存在
    interview = crud.interview.get(db=db, id=interview_id)
    if not interview:
        raise HTTPException(
            status_code=404,
            detail="面试不存在"
        )
    
    # 检查当前用户是否有权限
    if not crud.user.is_superuser(current_user) and current_user.id != interviewer_id:
        raise HTTPException(
            status_code=403, 
            detail="没有权限生成其他面试官的准备材料"
        )
    
    # 检查该面试官是否参与了这次面试
    interviewer_ids = [interviewer.id for interviewer in interview.interviewers]
    if interviewer_id not in interviewer_ids:
        raise HTTPException(
            status_code=400,
            detail="该面试官未参与此次面试"
        )
    
    # 获取候选人和职位信息用于生成准备材料
    resume = interview.resume
    job = interview.job
    
    if not resume or not job:
        raise HTTPException(
            status_code=400,
            detail="缺少简历或职位信息，无法生成准备材料"
        )
    
    # 生成面试准备材料（这里是简化版本）
    candidate_name = resume.name or "候选人"
    position = job.title or "该职位"
    
    preparation_notes = f"""# {candidate_name}面试准备材料

## 职位要求分析
- 分析{position}所需的关键技能和经验
- 准备针对性的技术问题
- 关注候选人简历中的技能匹配度

## 技术评估要点
1. 编码能力评估
   - 算法基础
   - 代码质量和规范
   - 问题解决思路

2. 系统设计能力
   - 架构设计原则
   - 性能和可扩展性考量
   - 技术选型的判断

3. 技术广度和深度
   - 对技术栈的熟悉程度
   - 对新技术的学习能力
   - 技术选型的判断力

## 行为面试问题
- 描述一个您克服的技术挑战
- 如何处理项目中的冲突
- 团队协作经历分享

## 候选人背景调研
- 之前公司的技术栈和项目规模
- 行业经验和领域知识
- 职业发展轨迹分析

## 准备的问题清单
1. 技术问题：根据职位要求设计相关问题
2. 项目经验问题：请候选人详细介绍最具挑战性的项目
3. 团队协作问题：如何处理团队分歧
4. 职业发展问题：为什么选择应聘我们公司
"""
    
    # 更新面试准备材料
    db.query(models.interview_interviewers).filter(
        models.interview_interviewers.c.interview_id == interview_id,
        models.interview_interviewers.c.interviewer_id == interviewer_id
    ).update({"preparation_notes": preparation_notes})
    db.commit()
    
    return {"status": "success", "preparation_notes": preparation_notes}


@router.get(
    "/{interview_id}",
    response_model=schemas.InterviewWithDetails,
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["interview_read"]
            )
        )
    ]
)
def read_interview(
    *,
    db: Session = Depends(deps.get_db),
    interview_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """获取单个面试详情"""
    interview = crud.interview.get(db=db, id=interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="面试不存在")
    
    # 检查租户权限
    resume = db.query(models.Resume).filter(models.Resume.id == interview.resume_id).first()
    if not current_user.is_superuser and resume and resume.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="无权查看该面试详情")
    
    # 序列化处理，将SQLAlchemy对象转换为可以JSON序列化的字典
    interview_dict = {
        "id": interview.id,
        "resume_id": interview.resume_id,
        "job_id": interview.job_id,
        "status": interview.status,
        "schedule_time": interview.schedule_time,
        "feedback": interview.feedback,
        "location": interview.location,
        "interview_type": interview.interview_type,
        "duration": interview.duration,
        "notes": interview.notes,
        "created_at": interview.created_at,
        "updated_at": interview.updated_at,
        "resume_title": None,  # 初始化resume_title
        "job_title": None,     # 初始化job_title
        "interviewer_names": []  # 初始化interviewer_names为空列表
    }
    
    # 处理Resume对象
    if hasattr(interview, "resume") and interview.resume:
        interview_dict["resume"] = {
            "id": interview.resume.id,
            "name": interview.resume.name,
            "phone": interview.resume.phone,
            "email": interview.resume.email,
            "gender": interview.resume.gender,
            "highest_education": interview.resume.highest_education,
            "major": interview.resume.major
        }
        # 更新resume_title
        interview_dict["resume_title"] = interview.resume.name
    
    # 处理Job对象
    if hasattr(interview, "job") and interview.job:
        interview_dict["job"] = {
            "id": interview.job.id,
            "title": interview.job.title,
            "department": getattr(interview.job, "department", None)
        }
        # 更新job_title
        interview_dict["job_title"] = interview.job.title
    
    # 处理面试官对象
    if hasattr(interview, "interviewers") and interview.interviewers:
        interview_dict["interviewers"] = []
        interview_dict["interviewer_names"] = []  # 面试官姓名列表
        for interviewer in interview.interviewers:
            interview_dict["interviewers"].append({
                "id": interviewer.id,
                "username": interviewer.username,
                "email": interviewer.email,
                "avatar": getattr(interviewer, "avatar", None)
            })
            # 添加面试官姓名到列表
            interview_dict["interviewer_names"].append(
                interviewer.username
            )
    
    # 直接返回符合模型结构的字典，不包装在data中
    return interview_dict


@router.get("/{interview_id}/preparation")
async def get_interview_preparation(
    *,
    db: Session = Depends(deps.get_db),
    interview_id: int,
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """获取面试准备信息"""
    # 使用服务层处理业务逻辑
    preparation_info = interview_service.get_interview_preparation(
        db=db,
        interview_id=interview_id,
        current_user=current_user
    )
    return preparation_info


@router.put("/{interview_id}/preparation")
async def update_interview_preparation(
    *,
    db: Session = Depends(deps.get_db),
    interview_id: int,
    data: Dict[str, Any],
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """更新面试准备信息"""
    # 使用服务层处理业务逻辑
    result = interview_service.update_interview_preparation(
        db=db,
        interview_id=interview_id,
        current_user=current_user,
        data=data
    )
    return result


@router.get("/interviewers/focus-points")
async def get_interviewer_focus_points(
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """获取面试官关注点列表"""
    # 使用服务层获取预定义的关注点列表
    return interview_service.get_interviewer_focus_points() 