from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from app.models.talent_pool import TalentPool, TalentPoolMember
from app.schemas.talent_pool import (
    TalentPoolCreate,
    TalentPoolUpdate,
    TalentPoolMemberCreate
)


class TalentPoolService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_pool(self, pool: TalentPoolCreate) -> TalentPool:
        """创建人才库"""
        db_pool = TalentPool(
            tenant_id=pool.tenant_id,
            pool_name=pool.pool_name,
            description=pool.description,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        self.db.add(db_pool)
        self.db.commit()
        self.db.refresh(db_pool)
        return db_pool
    
    def get_pool(self, pool_id: int) -> Optional[TalentPool]:
        """获取人才库详情"""
        query = self.db.query(TalentPool)
        return query.filter(TalentPool.pool_id == pool_id).first()
    
    def list_tenant_pools(self, tenant_id: int) -> List[TalentPool]:
        """获取租户的所有人才库"""
        return (self.db.query(TalentPool)
                .filter(TalentPool.tenant_id == tenant_id)
                .all())
    
    def update_pool(
        self,
        pool_id: int,
        pool: TalentPoolUpdate
    ) -> Optional[TalentPool]:
        """更新人才库信息"""
        db_pool = self.get_pool(pool_id)
        if not db_pool:
            return None
            
        update_data = pool.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_pool, field, value)
        
        db_pool.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_pool)
        return db_pool
    
    def delete_pool(self, pool_id: int) -> bool:
        """删除人才库"""
        db_pool = self.get_pool(pool_id)
        if not db_pool:
            return False
            
        self.db.delete(db_pool)
        self.db.commit()
        return True
    
    def add_member(self, member: TalentPoolMemberCreate) -> TalentPoolMember:
        """添加人才库成员"""
        db_member = TalentPoolMember(
            pool_id=member.pool_id,
            talent_id=member.talent_id,
            remark=member.remark,
            added_at=datetime.utcnow()
        )
        self.db.add(db_member)
        self.db.commit()
        self.db.refresh(db_member)
        return db_member
    
    def remove_member(self, member_id: int) -> bool:
        """移除人才库成员"""
        query = self.db.query(TalentPoolMember)
        db_member = (query
                    .filter(TalentPoolMember.member_id == member_id)
                    .first())
        if not db_member:
            return False
            
        self.db.delete(db_member)
        self.db.commit()
        return True
    
    def list_pool_members(self, pool_id: int) -> List[TalentPoolMember]:
        """获取人才库所有成员"""
        return (self.db.query(TalentPoolMember)
                .filter(TalentPoolMember.pool_id == pool_id)
                .all()) 