from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.get(
    "/",
    response_model=schemas.CandidateListResponse,
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["candidate_read"]
            )
        )
    ]
)
def read_candidates(
    db: Session = Depends(deps.get_db),
    page: int = Query(1, ge=1, description="页码"),
    per_page: int = Query(10, ge=1, le=100, description="每页数量"),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """获取候选人列表"""
    # 转换分页参数
    skip = (page - 1) * per_page
    
    # 获取数据和总数
    if current_user.is_superuser:
        candidates = crud.candidate.get_multi(db, skip=skip, limit=per_page)
        total = crud.candidate.count(db)
    else:
        candidates = crud.candidate.get_multi_by_tenant(
            db,
            tenant_id=current_user.tenant_id,
            skip=skip,
            limit=per_page
        )
        total = crud.candidate.count_by_tenant(
            db, 
            tenant_id=current_user.tenant_id
        )
    
    # 计算总页数
    total_pages = (total + per_page - 1) // per_page
    
    # 返回统一格式
    return {
        "data": candidates,
        "meta": {
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages
        }
    }


@router.post(
    "/",
    response_model=schemas.Candidate,
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["candidate_create"]
            )
        )
    ]
)
def create_candidate(
    *,
    db: Session = Depends(deps.get_db),
    candidate_in: schemas.CandidateCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """创建新候选人"""
    # 检查邮箱是否已存在
    candidate = crud.candidate.get_by_email(db, email=candidate_in.email)
    if candidate:
        raise HTTPException(
            status_code=400,
            detail="该邮箱已被注册"
        )
    
    # 创建候选人并关联到当前租户
    candidate = crud.candidate.create_with_tenant(
        db=db,
        obj_in=candidate_in,
        tenant_id=current_user.tenant_id
    )
    return candidate


@router.get(
    "/{candidate_id}", 
    response_model=schemas.CandidateWithInterviews,
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["candidate_read"]
            )
        )
    ]
)
def read_candidate(
    *,
    db: Session = Depends(deps.get_db),
    candidate_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """获取指定候选人信息"""
    candidate = crud.candidate.get(db=db, id=candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="候选人不存在")
    
    # 检查租户权限
    if not current_user.is_superuser and candidate.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="无权访问该候选人信息")
        
    return candidate


@router.put(
    "/{candidate_id}",
    response_model=schemas.Candidate,
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["candidate_update"]
            )
        )
    ]
)
def update_candidate(
    *,
    db: Session = Depends(deps.get_db),
    candidate_id: int,
    candidate_in: schemas.CandidateUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """更新候选人信息"""
    candidate = crud.candidate.get(db=db, id=candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="候选人不存在")
        
    # 检查租户权限
    if not current_user.is_superuser and candidate.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="无权更新该候选人信息")
    
    candidate = crud.candidate.update(
        db=db,
        db_obj=candidate,
        obj_in=candidate_in
    )
    return candidate


@router.delete(
    "/{candidate_id}",
    response_model=schemas.Candidate,
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["candidate_delete"]
            )
        )
    ]
)
def delete_candidate(
    *,
    db: Session = Depends(deps.get_db),
    candidate_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """删除候选人"""
    candidate = crud.candidate.get(db=db, id=candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="候选人不存在")
        
    # 检查租户权限
    if not current_user.is_superuser and candidate.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="无权删除该候选人")
        
    candidate = crud.candidate.remove(db=db, id=candidate_id)
    return candidate 