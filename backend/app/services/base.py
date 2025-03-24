from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.db.base_class import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    基础服务类,提供通用的CRUD操作
    """

    def __init__(self, model_class: Type[ModelType]):
        """
        初始化服务
        Args:
            model_class: SQLAlchemy模型类
        """
        self.model = model_class

    def get(
        self,
        db: Session,
        id: Any
    ) -> Optional[ModelType]:
        """
        根据ID获取记录
        """
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[List[Any]] = None,
        order_by: Optional[Any] = None
    ) -> List[ModelType]:
        """
        获取多条记录
        :param filters: SQLAlchemy过滤条件列表
        :param order_by: SQLAlchemy排序条件
        """
        query = db.query(self.model)
        
        if filters:
            query = query.filter(and_(*filters))
            
        if order_by is not None:
            query = query.order_by(order_by)
            
        return query.offset(skip).limit(limit).all()

    def get_multi_by_tenant(
        self,
        db: Session,
        *,
        tenant_id: int,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[List[Any]] = None,
        order_by: Optional[Any] = None
    ) -> List[ModelType]:
        """
        获取租户的多条记录
        """
        if not hasattr(self.model, 'tenant_id'):
            raise ValueError(f"{self.model.__name__} 没有 tenant_id 字段")
            
        tenant_filter = [self.model.tenant_id == tenant_id]
        if filters:
            tenant_filter.extend(filters)
            
        return self.get_multi(
            db,
            skip=skip,
            limit=limit,
            filters=tenant_filter,
            order_by=order_by
        )

    def create(
        self,
        db: Session,
        *,
        obj_in: CreateSchemaType
    ) -> ModelType:
        """
        创建记录
        """
        obj_in_data = obj_in.dict()
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """
        更新记录
        """
        obj_data = db_obj.__dict__
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
            
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
                
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(
        self,
        db: Session,
        *,
        id: int
    ) -> ModelType:
        """
        删除记录
        """
        obj = db.query(self.model).get(id)
        if not obj:
            raise HTTPException(status_code=404, detail="记录不存在")
            
        db.delete(obj)
        db.commit()
        return obj

    def exists(
        self,
        db: Session,
        *,
        id: int
    ) -> bool:
        """
        检查记录是否存在
        """
        return db.query(
            db.query(self.model).filter(self.model.id == id).exists()
        ).scalar()

    def count(
        self,
        db: Session,
        *,
        filters: Optional[List[Any]] = None
    ) -> int:
        """
        获取记录数量
        """
        query = db.query(self.model)
        if filters:
            query = query.filter(and_(*filters))
        return query.count()

    def get_by_field(
        self,
        db: Session,
        *,
        field: str,
        value: Any
    ) -> Optional[ModelType]:
        """
        根据字段获取记录
        """
        if not hasattr(self.model, field):
            raise ValueError(f"{self.model.__name__} 没有 {field} 字段")
            
        return db.query(self.model).filter(
            getattr(self.model, field) == value
        ).first()

    def get_multi_by_field(
        self,
        db: Session,
        *,
        field: str,
        value: Any,
        skip: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        """
        根据字段获取多条记录
        """
        if not hasattr(self.model, field):
            raise ValueError(f"{self.model.__name__} 没有 {field} 字段")
            
        return db.query(self.model).filter(
            getattr(self.model, field) == value
        ).offset(skip).limit(limit).all()


# 导出基类
__all__ = ["BaseService"] 