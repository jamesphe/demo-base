from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

from app.models.certification import Certification
from app.schemas.certification import CertificationCreate, CertificationUpdate
from .base import BaseService


class CertificationService(BaseService[Certification, CertificationCreate, 
                                       CertificationUpdate]):
    """证书服务"""
    
    def __init__(self):
        super().__init__(Certification)

    def get_certification(
        self, 
        db: Session, 
        certification_id: int
    ) -> Optional[Certification]:
        """获取单个证书"""
        return db.query(Certification).filter(
            Certification.id == certification_id
        ).first()

    def get_certifications(
        self, 
        db: Session, 
        tenant_id: Optional[int] = None,
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """获取证书列表"""
        query = db.query(Certification)
        
        # 应用租户过滤
        if tenant_id is not None:
            # 获取特定租户的证书和平台公共证书
            query = query.filter(
                (Certification.tenant_id == tenant_id) | 
                (Certification.tenant_id.is_(None))
            )
        
        # 应用其他过滤条件
        if filters:
            if filters.get("status"):
                query = query.filter(Certification.status == filters["status"])
            if filters.get("category"):
                query = query.filter(Certification.category == filters["category"])
            if filters.get("name"):
                query = query.filter(
                    Certification.name.ilike(f"%{filters['name']}%")
                )
            if filters.get("issuing_organization"):
                query = query.filter(
                    Certification.issuing_organization.ilike(
                        f"%{filters['issuing_organization']}%"
                    )
                )
        
        # 获取总数
        total = query.count()
        
        # 应用分页
        certifications = query.offset(skip).limit(limit).all()
        
        return {
            "total": total,
            "items": certifications
        }

    def create_certification(
        self,
        db: Session, 
        certification_in: CertificationCreate
    ) -> Certification:
        """创建新证书"""
        certification_data = jsonable_encoder(certification_in)
        certification = Certification(**certification_data)
        db.add(certification)
        db.commit()
        db.refresh(certification)
        return certification

    def update_certification(
        self, 
        db: Session, 
        certification: Certification,
        certification_in: CertificationUpdate
    ) -> Certification:
        """更新证书信息"""
        obj_data = jsonable_encoder(certification)
        update_data = certification_in.dict(exclude_unset=True)
        
        for field in obj_data:
            if field in update_data:
                setattr(certification, field, update_data[field])
        
        db.add(certification)
        db.commit()
        db.refresh(certification)
        return certification

    def delete_certification(
        self, 
        db: Session, 
        certification: Certification
    ) -> Certification:
        """删除证书"""
        # 软删除，将状态设置为inactive
        certification.status = "inactive"
        db.add(certification)
        db.commit()
        db.refresh(certification)
        return certification

    def hard_delete_certification(
        self, 
        db: Session, 
        certification: Certification
    ) -> None:
        """硬删除证书（从数据库中完全删除）"""
        db.delete(certification)
        db.commit()


# 创建服务实例
certification_service = CertificationService()

# 只导出实例
__all__ = ["certification_service"]