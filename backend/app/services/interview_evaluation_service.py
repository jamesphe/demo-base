from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app import models
from app.schemas.interview_evaluation import (
    InterviewEvaluationCreate,
    InterviewEvaluationUpdate
)
from app.models.interview import Interview
from app.models.interview_evaluation import InterviewEvaluation
from app.services.base import BaseService
from app.services.interview_service import interview_service
from app.services.job_service import job_service
from app.services.candidate_service import candidate_service


class InterviewEvaluationService(BaseService[
    InterviewEvaluation,
    InterviewEvaluationCreate,
    InterviewEvaluationUpdate
]):
    """面试评估服务"""

    async def create_evaluation(
        self,
        db: Session,
        *,
        evaluation_in: Dict[str, Any]
    ) -> Dict[str, Any]:
        """创建面试评估"""
        # 检查是否已存在评估
        existing_evaluation = await self.get_evaluation(
            db=db,
            interview_id=evaluation_in["interview_id"]
        )
        
        if existing_evaluation:
            # 如果已存在，则更新
            return await self.update_evaluation(
                db=db,
                interview_id=evaluation_in["interview_id"],
                evaluation_in=evaluation_in
            )
        
        # 获取面试信息
        interview = interview_service.get(
            db=db, 
            id=evaluation_in["interview_id"]
        )
        if not interview:
            raise HTTPException(
                status_code=404,
                detail="面试不存在"
            )
        
        # 准备评估数据
        db_obj = InterviewEvaluation(
            interview_id=evaluation_in["interview_id"],
            evaluator_id=evaluation_in["evaluator_id"],
            overall_score=evaluation_in["overall_score"],
            technical_score=evaluation_in.get("technical_score"),
            communication_score=evaluation_in.get("communication_score"),
            experience_score=evaluation_in.get("experience_score"),
            culture_fit_score=evaluation_in.get("culture_fit_score"),
            result=evaluation_in["result"],
            conclusion=evaluation_in["conclusion"],
            strengths=evaluation_in.get("strengths"),
            weaknesses=evaluation_in.get("weaknesses"),
            next_step=evaluation_in.get("next_step"),
            technical_comments=evaluation_in.get("technical_comments"),
            communication_comments=evaluation_in.get("communication_comments"),
            experience_comments=evaluation_in.get("experience_comments"),
            cultural_comments=evaluation_in.get("cultural_comments"),
            comments=evaluation_in.get("comments"),
            feedback_summary=evaluation_in.get("feedback_summary"),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        # 更新候选人状态
        if interview.candidate_id:
            candidate_status = self._map_result_to_candidate_status(
                evaluation_in["result"]
            )
            if candidate_status:
                await candidate_service.update_candidate_status(
                    db=db,
                    candidate_id=interview.candidate_id,
                    status=candidate_status,
                    note=f"面试评估: {evaluation_in['conclusion']}"
                )
        
        return self._prepare_evaluation_response(db_obj, db)

    async def update_evaluation(
        self,
        db: Session,
        *,
        interview_id: int,
        evaluation_in: Dict[str, Any]
    ) -> Dict[str, Any]:
        """更新面试评估"""
        evaluation = db.query(InterviewEvaluation).filter(
            InterviewEvaluation.interview_id == interview_id
        ).first()
        
        if not evaluation:
            raise HTTPException(
                status_code=404,
                detail="面试评估不存在"
            )
        
        # 更新评估字段
        for field, value in evaluation_in.items():
            if hasattr(evaluation, field) and value is not None:
                setattr(evaluation, field, value)
        
        evaluation.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(evaluation)
        
        # 如果结果变更，更新候选人状态
        interview = interview_service.get(db=db, id=interview_id)
        if interview and interview.candidate_id and "result" in evaluation_in:
            candidate_status = self._map_result_to_candidate_status(
                evaluation_in["result"]
            )
            if candidate_status:
                await candidate_service.update_candidate_status(
                    db=db,
                    candidate_id=interview.candidate_id,
                    status=candidate_status,
                    note=f"面试评估更新: {evaluation_in.get('conclusion', evaluation.conclusion)}"
                )
        
        return self._prepare_evaluation_response(evaluation, db)

    async def get_evaluation(
        self,
        db: Session,
        *,
        interview_id: int
    ) -> Optional[Dict[str, Any]]:
        """获取面试评估"""
        evaluation = db.query(InterviewEvaluation).filter(
            InterviewEvaluation.interview_id == interview_id
        ).first()
        
        if not evaluation:
            return None
        
        return self._prepare_evaluation_response(evaluation, db)

    def _prepare_evaluation_response(
        self,
        evaluation: InterviewEvaluation,
        db: Session
    ) -> Dict[str, Any]:
        """准备评估响应数据"""
        # 获取评估人信息
        evaluator = None
        if evaluation.evaluator_id:
            evaluator = db.query(models.User).filter(
                models.User.id == evaluation.evaluator_id
            ).first()
        
        response = {
            "id": evaluation.id,
            "interview_id": evaluation.interview_id,
            "evaluator_id": evaluation.evaluator_id,
            "evaluator_name": evaluator.username if evaluator else None,
            "overall_score": evaluation.overall_score,
            "technical_score": evaluation.technical_score,
            "communication_score": evaluation.communication_score,
            "experience_score": evaluation.experience_score,
            "culture_fit_score": evaluation.culture_fit_score,
            "result": evaluation.result,
            "conclusion": evaluation.conclusion,
            "strengths": evaluation.strengths,
            "weaknesses": evaluation.weaknesses,
            "next_step": evaluation.next_step,
            "technical_comments": evaluation.technical_comments,
            "communication_comments": evaluation.communication_comments,
            "experience_comments": evaluation.experience_comments,
            "cultural_comments": evaluation.cultural_comments,
            "comments": evaluation.comments,
            "feedback_summary": evaluation.feedback_summary,
            "created_at": evaluation.created_at,
            "updated_at": evaluation.updated_at
        }
        
        return response

    def _map_result_to_candidate_status(self, result: str) -> Optional[str]:
        """将评估结果映射到候选人状态"""
        result_map = {
            "通过": "approved",
            "不通过": "rejected",
            "待定": "pending",
            "复试": "interviewing",
            "终试": "interviewing",
            "发offer": "offer_pending"
        }
        return result_map.get(result)

    async def generate_next_steps(
        self,
        db: Session,
        *,
        interview: Interview,
        evaluation: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """生成下一步选项"""
        result = evaluation.get("result", "")
        interview_type = interview.type
        
        next_steps = []
        
        # 通过的情况
        if result in ["通过", "复试", "终试"]:
            # 如果是初试，则可以安排复试
            if interview_type == "first":
                next_steps.append({
                    "action": "schedule_next_interview",
                    "label": "安排复试",
                    "description": "安排候选人进行复试",
                    "icon": "el-icon-date",
                    "type": "primary",
                    "params": {
                        "interview_type": "second",
                        "candidate_id": interview.candidate_id,
                        "job_id": interview.job_id
                    }
                })
            
            # 如果是复试，则可以安排终试
            elif interview_type == "second":
                next_steps.append({
                    "action": "schedule_next_interview",
                    "label": "安排终试",
                    "description": "安排候选人进行终试",
                    "icon": "el-icon-date",
                    "type": "success",
                    "params": {
                        "interview_type": "final",
                        "candidate_id": interview.candidate_id,
                        "job_id": interview.job_id
                    }
                })
            
            # 如果是终试，则可以发送offer
            elif interview_type == "final":
                next_steps.append({
                    "action": "send_offer",
                    "label": "发送Offer",
                    "description": "向候选人发送录用意向书",
                    "icon": "el-icon-document",
                    "type": "success",
                    "params": {
                        "candidate_id": interview.candidate_id,
                        "job_id": interview.job_id
                    }
                })
        
        # 不通过的情况
        if result == "不通过":
            next_steps.append({
                "action": "reject_candidate",
                "label": "发送拒绝通知",
                "description": "向候选人发送婉拒通知",
                "icon": "el-icon-close",
                "type": "danger",
                "params": {
                    "candidate_id": interview.candidate_id,
                    "reason": evaluation.get("conclusion")
                }
            })
        
        # 通用选项
        next_steps.append({
            "action": "add_notes",
            "label": "添加备注",
            "description": "为此次面试添加额外备注信息",
            "icon": "el-icon-edit",
            "type": "info",
            "params": {}
        })
        
        return next_steps

    async def execute_next_step(
        self,
        db: Session,
        *,
        interview_id: int,
        next_step: Dict[str, Any],
        current_user: models.User
    ) -> Dict[str, Any]:
        """执行下一步操作"""
        action = next_step.get("action")
        params = next_step.get("params", {})
        
        if not action:
            raise HTTPException(
                status_code=400,
                detail="未指定操作类型"
            )
        
        # 获取面试信息
        interview = interview_service.get(db=db, id=interview_id)
        if not interview:
            raise HTTPException(
                status_code=404,
                detail="面试不存在"
            )
        
        # 根据不同操作执行相应逻辑
        result = {}
        
        if action == "schedule_next_interview":
            # 安排下一轮面试
            result = await self._schedule_next_interview(
                db=db,
                interview=interview,
                params=params,
                current_user=current_user
            )
        
        elif action == "send_offer":
            # 发送offer
            result = await self._send_offer(
                db=db,
                interview=interview,
                params=params,
                current_user=current_user
            )
        
        elif action == "reject_candidate":
            # 拒绝候选人
            result = await self._reject_candidate(
                db=db,
                interview=interview,
                params=params,
                current_user=current_user
            )
        
        elif action == "add_notes":
            # 添加备注
            result = await self._add_notes(
                db=db,
                interview=interview,
                params=params,
                current_user=current_user
            )
        
        else:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的操作类型: {action}"
            )
        
        return result

    async def _schedule_next_interview(
        self,
        db: Session,
        *,
        interview: Interview,
        params: Dict[str, Any],
        current_user: models.User
    ) -> Dict[str, Any]:
        """安排下一轮面试"""
        from app.schemas.interview import InterviewCreate
        
        interview_type = params.get("interview_type")
        if not interview_type:
            raise HTTPException(
                status_code=400,
                detail="未指定面试类型"
            )
        
        # 创建下一轮面试
        interview_data = InterviewCreate(
            tenant_id=interview.tenant_id,
            candidate_id=interview.candidate_id,
            job_id=interview.job_id,
            resume_id=interview.resume_id,
            type=interview_type,
            status="scheduled",
            created_by=current_user.id
        )
        
        new_interview = await interview_service.create(
            db=db,
            obj_in=interview_data
        )
        
        return {
            "interview_id": new_interview.id,
            "message": f"已成功安排{self._get_interview_type_text(interview_type)}"
        }

    async def _send_offer(
        self,
        db: Session,
        *,
        interview: Interview,
        params: Dict[str, Any],
        current_user: models.User
    ) -> Dict[str, Any]:
        """发送offer"""
        from app.services.offer_service import offer_service
        from app.schemas.offer import OfferCreate
        
        # 创建Offer
        offer_data = OfferCreate(
            tenant_id=interview.tenant_id,
            candidate_id=interview.candidate_id,
            job_id=interview.job_id,
            resume_id=interview.resume_id,
            status="draft",
            created_by=current_user.id
        )
        
        offer = await offer_service.create_offer(
            db=db,
            offer_in=offer_data
        )
        
        # 更新候选人状态
        await candidate_service.update_candidate_status(
            db=db,
            candidate_id=interview.candidate_id,
            status="offer_pending",
            note="已创建Offer"
        )
        
        return {
            "offer_id": offer.id,
            "message": "已成功创建Offer，请前往Offer管理页面完善详情"
        }

    async def _reject_candidate(
        self,
        db: Session,
        *,
        interview: Interview,
        params: Dict[str, Any],
        current_user: models.User
    ) -> Dict[str, Any]:
        """拒绝候选人"""
        reason = params.get("reason", "不符合岗位要求")
        
        # 更新候选人状态
        await candidate_service.update_candidate_status(
            db=db,
            candidate_id=interview.candidate_id,
            status="rejected",
            note=f"拒绝原因: {reason}"
        )
        
        # 可以在这里添加发送拒绝邮件的逻辑
        
        return {
            "message": "已拒绝候选人"
        }

    async def _add_notes(
        self,
        db: Session,
        *,
        interview: Interview,
        params: Dict[str, Any],
        current_user: models.User
    ) -> Dict[str, Any]:
        """添加备注"""
        notes = params.get("notes", "")
        
        if not notes:
            raise HTTPException(
                status_code=400,
                detail="备注内容不能为空"
            )
        
        # 添加面试备注
        interview_service.update_interview(
            db=db,
            id=interview.id,
            obj_in={"notes": notes}
        )
        
        return {
            "message": "备注已添加"
        }

    def _get_interview_type_text(self, interview_type: str) -> str:
        """获取面试类型的中文描述"""
        type_map = {
            "first": "初试",
            "second": "复试",
            "final": "终试"
        }
        return type_map.get(interview_type, "面试")


# 创建服务实例
interview_evaluation_service = InterviewEvaluationService(InterviewEvaluation) 