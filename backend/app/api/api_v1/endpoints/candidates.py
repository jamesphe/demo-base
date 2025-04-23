from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.get(
    "",
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


@router.get(
    "/list",
    response_model=schemas.CandidateListResponse,
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["candidate_read"]
            )
        )
    ]
)
def list_candidates(
    db: Session = Depends(deps.get_db),
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(10, ge=1, le=100, description="每页数量"),
    name: Optional[str] = Query(None, description="候选人姓名"),
    phone: Optional[str] = Query(None, description="联系电话"),
    email: Optional[str] = Query(None, description="邮箱"),
    status: Optional[int] = Query(None, description="状态"),
    startDate: Optional[str] = Query(None, description="开始日期"),
    endDate: Optional[str] = Query(None, description="结束日期"),
    sort_field: Optional[str] = Query(None, description="排序字段"),
    sort_order: Optional[str] = Query(None, description="排序方向"),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """获取候选人列表，支持排序和筛选"""
    # 转换分页参数
    skip = (page - 1) * limit
    
    # 构建过滤条件
    filters = {}
    if name:
        filters["name"] = name
    if phone:
        filters["phone"] = phone
    if email:
        filters["email"] = email
    if status:
        filters["status"] = status
    # 添加日期过滤条件
    date_filters = {}
    if startDate:
        date_filters["start_date"] = startDate
    if endDate:
        date_filters["end_date"] = endDate
    
    # 构建排序条件
    sort_by = None
    if sort_field:
        sort_by = (sort_field, sort_order or "asc")
    
    # 获取数据和总数
    if current_user.is_superuser:
        candidates = crud.candidate.get_multi_with_filters(
            db, 
            skip=skip, 
            limit=limit,
            filters=filters,
            date_filters=date_filters,
            sort_by=sort_by,
            include_relations=True  # 添加关联数据加载
        )
        total = crud.candidate.count_with_filters(
            db,
            filters=filters,
            date_filters=date_filters
        )
    else:
        filters["tenant_id"] = current_user.tenant_id
        candidates = crud.candidate.get_multi_with_filters(
            db,
            skip=skip,
            limit=limit,
            filters=filters,
            date_filters=date_filters,
            sort_by=sort_by,
            include_relations=True  # 添加关联数据加载
        )
        total = crud.candidate.count_with_filters(
            db,
            filters=filters,
            date_filters=date_filters
        )
    
    # 计算总页数
    total_pages = (total + limit - 1) // limit
    
    # 返回统一格式
    return {
        "data": candidates,
        "meta": {
            "total": total,
            "page": page,
            "per_page": limit,
            "total_pages": total_pages
        }
    }


@router.post(
    "",
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
    if (not current_user.is_superuser and 
            candidate.tenant_id != current_user.tenant_id):
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
    if (not current_user.is_superuser and 
            candidate.tenant_id != current_user.tenant_id):
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
    if (not current_user.is_superuser and 
            candidate.tenant_id != current_user.tenant_id):
        raise HTTPException(status_code=403, detail="无权删除该候选人")
        
    candidate = crud.candidate.remove(db=db, id=candidate_id)
    return candidate


@router.put(
    "/batch-update",
    response_model=list[schemas.Candidate],
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["candidate_update"]
            )
        )
    ]
)
def batch_update_candidate_status(
    *,
    db: Session = Depends(deps.get_db),
    batch_update: schemas.CandidateBatchUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """批量更新候选人状态"""
    if not batch_update.candidate_ids:
        raise HTTPException(status_code=400, detail="未提供候选人ID列表")
    
    if batch_update.status is None:
        raise HTTPException(status_code=400, detail="未提供更新的状态值")
    
    updated_candidates = []
    for candidate_id in batch_update.candidate_ids:
        candidate = crud.candidate.get(db=db, id=candidate_id)
        if not candidate:
            continue
            
        # 检查租户权限
        if (not current_user.is_superuser and 
                candidate.tenant_id != current_user.tenant_id):
            continue
        
        # 更新状态
        updated = crud.candidate.update(
            db=db,
            db_obj=candidate,
            obj_in=schemas.CandidateUpdate(status=batch_update.status)
        )
        updated_candidates.append(updated)
    
    return updated_candidates 