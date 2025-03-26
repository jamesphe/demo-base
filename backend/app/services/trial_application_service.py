from datetime import datetime, timedelta
from typing import Any, Dict

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.utils.security import generate_random_password


class TrialApplicationService:
    @staticmethod
    def apply_for_trial(
        db: Session, 
        application_data: Dict[str, Any]
    ) -> models.TrialApplication:
        """处理试用申请"""
        email = application_data.get("email")
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
        trial_id: int
    ) -> models.TrialApplication:
        """审批通过试用申请"""
        trial = crud.trial_application.get(db, id=trial_id)
        if not trial:
            raise HTTPException(status_code=404, detail="试用申请不存在")
        
        if trial.status != "pending":
            raise HTTPException(status_code=400, detail="只能审批待处理的申请")
        
        # 创建用户账号
        user_in = schemas.UserCreate(
            email=trial.contact_email,
            username=trial.company_name,
            password=generate_random_password(length=8),
            is_active=True,
            user_type="tenant"
        )
        user = crud.user.create(db, obj_in=user_in)
        
        # 设置试用期为14天
        start_date = datetime.now()
        end_date = start_date + timedelta(days=14)
        
        # 更新试用申请状态
        trial_update = schemas.TrialApplicationUpdate(
            status="active",
            trial_start_date=start_date,
            trial_end_date=end_date,
            user_id=user.id
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