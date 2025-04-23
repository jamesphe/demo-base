from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from app.crud.base import CRUDBase
from app.models.candidate import Candidate
from app.schemas.candidate import CandidateCreate, CandidateUpdate


class CRUDCandidate(CRUDBase[Candidate, CandidateCreate, CandidateUpdate]):
    def get_by_email(self, db: Session, *, email: str) -> Optional[Candidate]:
        return db.query(Candidate).filter(Candidate.email == email).first()

    def get_by_status(
        self, db: Session, *, status: str, skip: int = 0, limit: int = 100
    ) -> List[Candidate]:
        return (
            db.query(Candidate)
            .filter(Candidate.status == status)
            .offset(skip)
            .limit(limit)
            .all()
        )
        
    def get_multi_by_tenant(
        self,
        db: Session,
        *,
        tenant_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Candidate]:
        """获取指定租户的候选人列表"""
        return (
            db.query(Candidate)
            .filter(Candidate.tenant_id == tenant_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create_with_tenant(
        self,
        db: Session,
        *,
        obj_in: CandidateCreate,
        tenant_id: int
    ) -> Candidate:
        """创建带有租户ID的候选人"""
        obj_in_data = obj_in.dict()
        db_obj = Candidate(**obj_in_data, tenant_id=tenant_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
        
    def count_by_tenant(self, db: Session, *, tenant_id: int) -> int:
        """计算指定租户的候选人数量"""
        return db.query(Candidate).filter(Candidate.tenant_id == tenant_id).count()
        
    def get_multi_with_filters(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Dict[str, Any] = None,
        date_filters: Dict[str, str] = None,
        sort_by: Optional[Tuple[str, str]] = None,
        include_relations: bool = False
    ) -> List[Candidate]:
        """获取候选人列表，支持过滤和排序"""
        query = db.query(Candidate)
        
        # 加载关联数据
        if include_relations:
            query = query.outerjoin(Candidate.job).outerjoin(Candidate.primary_resume)
        
        # 应用过滤条件
        if filters:
            for field, value in filters.items():
                if value is not None:
                    # 处理模糊查询
                    if field == "name" and value:
                        query = query.filter(Candidate.name.ilike(f"%{value}%"))
                    elif field == "phone" and value:
                        query = query.filter(Candidate.phone.ilike(f"%{value}%"))
                    elif field == "email" and value:
                        query = query.filter(Candidate.email.ilike(f"%{value}%"))
                    else:
                        # 精确匹配
                        query = query.filter(getattr(Candidate, field) == value)
        
        # 应用日期过滤
        if date_filters:
            if "start_date" in date_filters and date_filters["start_date"]:
                start = date_filters["start_date"]
                query = query.filter(Candidate.created_at >= start)
            if "end_date" in date_filters and date_filters["end_date"]:
                end = date_filters["end_date"]
                query = query.filter(Candidate.created_at <= end)
        
        # 应用排序
        if sort_by:
            field, order = sort_by
            if hasattr(Candidate, field):
                column = getattr(Candidate, field)
                query = query.order_by(desc(column) if order == "desc" else asc(column))
        else:
            # 默认排序：按更新时间降序
            query = query.order_by(desc(Candidate.updated_at))
        
        # 应用分页
        return query.offset(skip).limit(limit).all()
    
    def count_with_filters(
        self,
        db: Session,
        *,
        filters: Dict[str, Any] = None,
        date_filters: Dict[str, str] = None
    ) -> int:
        """计算符合过滤条件的候选人数量"""
        query = db.query(Candidate)
        
        # 应用过滤条件
        if filters:
            for field, value in filters.items():
                if value is not None:
                    # 处理模糊查询
                    if field == "name" and value:
                        query = query.filter(Candidate.name.ilike(f"%{value}%"))
                    elif field == "phone" and value:
                        query = query.filter(Candidate.phone.ilike(f"%{value}%"))
                    elif field == "email" and value:
                        query = query.filter(Candidate.email.ilike(f"%{value}%"))
                    else:
                        # 精确匹配
                        query = query.filter(getattr(Candidate, field) == value)
        
        # 应用日期过滤
        if date_filters:
            if "start_date" in date_filters and date_filters["start_date"]:
                start = date_filters["start_date"]
                query = query.filter(Candidate.created_at >= start)
            if "end_date" in date_filters and date_filters["end_date"]:
                end = date_filters["end_date"]
                query = query.filter(Candidate.created_at <= end)
        
        return query.count()


candidate = CRUDCandidate(Candidate) 