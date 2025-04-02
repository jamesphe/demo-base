from datetime import datetime, timedelta
from typing import Any, Dict, List

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.utils.security import generate_random_password
from app.services.user_service import user_service


class TrialApplicationService:
    @staticmethod
    def apply_for_trial(
        db: Session, 
        application_data: Dict[str, Any]
    ) -> models.TrialApplication:
        """处理试用申请"""
        email = application_data.get("contact_email")
        company_name = application_data.get("company_name")
        contact_phone = application_data.get("contact_phone")
        
        # 检查邮箱是否已经存在
        if crud.user.get_by_email(db, email=email):
            raise HTTPException(
                status_code=400,
                detail="该邮箱已被注册"
            )
        
        # 检查公司名是否已存在
        existing_company = crud.trial_application.get_by_company_name(db, company_name=company_name)
        if existing_company:
            raise HTTPException(
                status_code=400,
                detail="该公司名已申请过试用"
            )
        
        # 检查联系人手机是否已存在
        existing_phone = crud.trial_application.get_by_contact_phone(db, contact_phone=contact_phone)
        if existing_phone:
            raise HTTPException(
                status_code=400,
                detail="该手机号已申请过试用"
            )
        
        # 检查是否有未完成的申请
        existing_trial = crud.trial_application.get_by_email(db, email=email)
        if existing_trial:
            if existing_trial.status == "pending":
                raise HTTPException(
                    status_code=400,
                    detail="您已有待处理的申请"
                )
            elif existing_trial.status == "active":
                raise HTTPException(
                    status_code=400,
                    detail="您已经在试用中"
                )
            elif (existing_trial.status == "expired" and
                  (datetime.now() - existing_trial.trial_end_date).days < 30):
                raise HTTPException(
                    status_code=400,
                    detail="您的试用已结束，30天后才能再次申请"
                )
        
        # 创建新的试用申请
        trial_in = schemas.TrialApplicationCreate(**application_data)
        return crud.trial_application.create(db=db, obj_in=trial_in)

    @staticmethod
    def get_trial_status(
        db: Session, 
        current_user: models.User
    ) -> schemas.TrialStatus:
        """获取试用状态"""
        trial = crud.trial_application.get_by_user_id(
            db, 
            user_id=current_user.id
        )
        if not trial:
            return schemas.TrialStatus(status="none")
        
        # 检查是否已过期
        if (trial.status == "active" and trial.trial_end_date and
                trial.trial_end_date < datetime.now()):
            trial_update = schemas.TrialApplicationUpdate(status="expired")
            trial = crud.trial_application.update(
                db, 
                db_obj=trial, 
                obj_in=trial_update
            )
        
        return schemas.TrialStatus(
            status=trial.status,
            created_at=trial.created_at,
            trial_start_date=trial.trial_start_date,
            trial_end_date=trial.trial_end_date,
            reject_reason=trial.reject_reason,
            company_name=trial.company_name,
            contact_name=trial.contact_name
        )

    @staticmethod
    def approve_trial(
        db: Session, 
        trial_id: int,
        approval_data: Dict[str, Any]
    ) -> models.TrialApplication:
        """审批通过试用申请"""
        trial = crud.trial_application.get(db, id=trial_id)
        if not trial:
            raise HTTPException(status_code=404, detail="试用申请不存在")
        
        if trial.status != "pending":
            raise HTTPException(status_code=400, detail="只能审批待处理的申请")
        
        # 验证邮箱是否已被使用
        if crud.user.get_by_email(db, email=approval_data["admin"]["email"]):
            raise HTTPException(
                status_code=400,
                detail="管理员邮箱已被使用"
            )
        
        # 创建租户
        tenant_data = approval_data["tenant"]
        tenant_in = schemas.TenantCreate(
            tenant_name=tenant_data["name"],
            contact_person=tenant_data["contact_person"],
            phone=tenant_data["phone"],
            email=tenant_data["email"],
            address=tenant_data["address"],
            status="active"
        )
        tenant = crud.tenant.create(db, obj_in=tenant_in)
        
        # 创建管理员账号
        admin_data = approval_data["admin"]
        user_in = schemas.UserCreate(
            email=admin_data["email"],
            username=admin_data["username"],
            password=admin_data["password"],
            is_active=True,
            user_type="tenant",
            tenant_id=tenant.id
        )
        user = crud.user.create(db, obj_in=user_in)
        
        # 获取租户管理员角色并分配给新用户
        tenant_admin_role = crud.role.get_by_name(db, name="tenant_admin")
        if tenant_admin_role:
            user_service.add_user_role(
                db,
                user_id=user.id,
                role_id=tenant_admin_role.id,
                current_user=user  # 这里传入新创建的用户作为当前用户
            )
        
        # 设置试用期
        start_date = datetime.strptime(approval_data["trial_start_date"], "%Y-%m-%d")
        end_date = start_date + timedelta(days=approval_data["trial_days"])
        
        # 更新试用申请状态
        trial_update = schemas.TrialApplicationUpdate(
            status="active",
            trial_start_date=start_date,
            trial_end_date=end_date,
            user_id=user.id,
            tenant_id=tenant.id
        )
        return crud.trial_application.update(
            db, 
            db_obj=trial, 
            obj_in=trial_update
        )

    @staticmethod
    def reject_trial(
        db: Session, 
        trial_id: int, 
        reason: str
    ) -> models.TrialApplication:
        """拒绝试用申请"""
        trial = crud.trial_application.get(db, id=trial_id)
        if not trial:
            raise HTTPException(status_code=404, detail="试用申请不存在")
        
        if trial.status != "pending":
            raise HTTPException(status_code=400, detail="只能拒绝待处理的申请")
        
        trial_update = schemas.TrialApplicationUpdate(
            status="rejected",
            reject_reason=reason
        )
        return crud.trial_application.update(
            db, 
            db_obj=trial, 
            obj_in=trial_update
        )

    @staticmethod
    def get_pending_trials(
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> list[models.TrialApplication]:
        """获取待审核的试用申请列表"""
        return crud.trial_application.get_pending_applications(
            db, 
            skip=skip, 
            limit=limit
        )

    @staticmethod
    def get_trial_list(db: Session, skip: int = 0, limit: int = 100) -> List[models.TrialApplication]:
        """获取所有试用申请记录"""
        return db.query(models.TrialApplication)\
            .order_by(models.TrialApplication.id.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()

    @staticmethod
    def get_pending_trials_with_count(
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[models.TrialApplication], int]:
        """获取待审核的试用申请列表及总数"""
        # 获取数据
        trials = crud.trial_application.get_pending_applications(
            db, 
            skip=skip, 
            limit=limit
        )
        
        # 获取总数
        total = db.query(models.TrialApplication).filter(
            models.TrialApplication.status == "pending"
        ).count()
        
        return trials, total

    @staticmethod
    def get_trial_list_with_count(
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[models.TrialApplication], int]:
        """获取所有试用申请记录及总数"""
        # 获取数据
        trials = db.query(models.TrialApplication)\
            .order_by(models.TrialApplication.id.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()
        
        # 获取总数
        total = db.query(models.TrialApplication).count()
        
        return trials, total