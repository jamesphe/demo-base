from typing import Optional, Union, List
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.tenant import Tenant
from app.schemas.tenant import TenantCreate, TenantUpdate


class CRUDTenant(CRUDBase[Tenant, TenantCreate, TenantUpdate]):
    def get_by_name(self, db: Session, *, tenant_name: str) -> Optional[Tenant]:
        return db.query(Tenant).filter(
            Tenant.tenant_name == tenant_name
        ).first()

    def get_by_external_id(self, db: Session, *, external_id: str) -> Optional[Tenant]:
        return db.query(Tenant).filter(
            Tenant.external_id == external_id
        ).first()

    def count(self, db: Session) -> int:
        """获取租户总数"""
        return db.query(self.model).count()


tenant = CRUDTenant(Tenant) 