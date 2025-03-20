from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.resume import Resume
from app.schemas.resume import ResumeCreate, ResumeUpdate
from datetime import datetime


class CRUDResume(CRUDBase[Resume, ResumeCreate, ResumeUpdate]):
    def get_by_resume_id(self, db: Session, *, resume_id: str) -> Optional[Resume]:
        return db.query(Resume).filter(Resume.resume_id == resume_id).first()

    def get_by_repository(
        self,
        db: Session,
        *,
        repository_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Resume]:
        return (
            db.query(Resume)
            .filter(Resume.repository_id == repository_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_status(
        self,
        db: Session,
        *,
        status: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Resume]:
        return (
            db.query(Resume)
            .filter(Resume.processing_status == status)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_candidate(
        self,
        db: Session,
        *,
        candidate_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Resume]:
        return (
            db.query(Resume)
            .filter(Resume.candidate_id == candidate_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count(self, db: Session) -> int:
        return db.query(Resume).count()

    def count_by_tenant(self, db: Session, tenant_id: int) -> int:
        return db.query(Resume).filter(Resume.tenant_id == tenant_id).count()

    def get_by_review_status(
        self, db: Session, status: str, skip: int = 0, limit: int = 100
    ) -> List[Resume]:
        """获取指定审核状态的简历"""
        return db.query(self.model)\
            .filter(self.model.review_status == status)\
            .offset(skip)\
            .limit(limit)\
            .all()

    def get_by_review_status_and_tenant(
        self, db: Session, status: str, tenant_id: int, skip: int = 0, limit: int = 100
    ) -> List[Resume]:
        """获取指定租户和审核状态的简历"""
        return db.query(self.model)\
            .filter(self.model.review_status == status)\
            .filter(self.model.tenant_id == tenant_id)\
            .offset(skip)\
            .limit(limit)\
            .all()

    def get_by_publisher(
        self, db: Session, publisher_id: int, skip: int = 0, limit: int = 100
    ) -> List[Resume]:
        """获取指定发布者的简历"""
        return db.query(self.model)\
            .filter(self.model.publisher_id == publisher_id)\
            .offset(skip)\
            .limit(limit)\
            .all()

    def get_multi_by_tenant(
        self, db: Session, *, tenant_id: int, skip: int = 0, limit: int = 100
    ) -> List[Resume]:
        """
        获取特定租户的所有简历，带分页
        """
        return db.query(self.model)\
            .filter(self.model.tenant_id == tenant_id)\
            .offset(skip)\
            .limit(limit)\
            .all()

    def create(self, db: Session, *, obj_in: ResumeCreate) -> Resume:
        """创建简历"""
        # 处理复杂结构（如工作经历、教育经历等）
        if isinstance(obj_in, dict):
            obj_data = obj_in
        else:
            obj_data = obj_in.model_dump(exclude_unset=True)
        
        # 处理JSON字段
        for field in ["work_history", "edu_experience", "awards", "skills", "certificates"]:
            if field in obj_data and obj_data[field] is not None:
                # 将Pydantic模型列表转换为字典列表
                if not isinstance(obj_data[field], list):
                    continue
                
                processed_items = []
                for item in obj_data[field]:
                    if hasattr(item, "model_dump"):
                        processed_items.append(item.model_dump())
                    else:
                        processed_items.append(item)
                obj_data[field] = processed_items
        
        # 设置时间戳
        now = datetime.utcnow()
        if "created_at" not in obj_data:
            obj_data["created_at"] = now
        if "updated_at" not in obj_data:
            obj_data["updated_at"] = now
        if "publish_time" not in obj_data:
            obj_data["publish_time"] = now
        
        # 设置处理状态
        if "processing_status" not in obj_data:
            obj_data["processing_status"] = "completed" if not obj_data.get("file_path") else "pending"
        
        # 创建数据库对象
        db_obj = self.model(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_without_repository(
        self,
        db: Session,
        *,
        tenant_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Resume]:
        """获取没有关联简历库的简历"""
        query = db.query(self.model).filter(self.model.repository_id.is_(None))
        
        if tenant_id is not None:
            query = query.filter(self.model.tenant_id == tenant_id)
        
        return query.offset(skip).limit(limit).all()

    def get_multi_with_filters(
        self,
        db: Session,
        *,
        tenant_id: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Resume]:
        """
        获取符合过滤条件的简历列表
        
        Args:
            db: 数据库会话
            tenant_id: 租户ID
            filters: 过滤条件字典
            skip: 跳过记录数
            limit: 返回记录数上限
            
        Returns:
            符合条件的简历列表
        """
        query = db.query(self.model)
        
        # 应用租户过滤
        if tenant_id is not None:
            query = query.filter(self.model.tenant_id == tenant_id)
        
        # 应用其他过滤条件
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field) and value is not None:
                    # 对字符串字段进行模糊匹配
                    if isinstance(value, str) and field in ["name", "phone", "email"]:
                        query = query.filter(getattr(self.model, field).ilike(f"%{value}%"))
                    else:
                        query = query.filter(getattr(self.model, field) == value)
        
        # 按创建时间降序排序
        query = query.order_by(self.model.created_at.desc())
        
        # 分页
        return query.offset(skip).limit(limit).all()

    def get_multi_with_filters_count(
        self,
        db: Session,
        *,
        tenant_id: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        获取符合过滤条件的简历总数
        
        Args:
            db: 数据库会话
            tenant_id: 租户ID
            filters: 过滤条件字典
            
        Returns:
            符合条件的简历总数
        """
        query = db.query(self.model)
        
        # 应用租户过滤
        if tenant_id is not None:
            query = query.filter(self.model.tenant_id == tenant_id)
        
        # 应用其他过滤条件
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field) and value is not None:
                    # 对字符串字段进行模糊匹配
                    if isinstance(value, str) and field in ["name", "phone", "email"]:
                        query = query.filter(getattr(self.model, field).ilike(f"%{value}%"))
                    else:
                        query = query.filter(getattr(self.model, field) == value)
        
        return query.count()


resume = CRUDResume(Resume) 