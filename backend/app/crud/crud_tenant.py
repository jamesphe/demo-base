from typing import Optional
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.tenant import Tenant
from app.schemas.tenant import TenantCreate, TenantUpdate


class CRUDTenant(CRUDBase[Tenant, TenantCreate, TenantUpdate]):
    def get_by_name(self, db: Session, *, name: str) -> Optional[Tenant]:
        return db.query(Tenant).filter(Tenant.tenant_name == name).first()


tenant = CRUDTenant(Tenant) 