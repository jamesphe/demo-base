from typing import Any, Dict
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.api import deps
from app.services.interview_ai_service import interview_ai_service
from app.schemas.interview import InterviewGuideRequest


router = APIRouter()


@router.post("/interview/guide")
async def generate_interview_guide(
    *,
    db: Session = Depends(deps.get_db),
    request: InterviewGuideRequest
) -> Dict[str, Any]:
    """生成面试指导文档"""
    return await interview_ai_service.generate_interview_guide_two_stage(db, request)


@router.post("/interview/guide/stream")
async def stream_interview_guide(
    *,
    db: Session = Depends(deps.get_db),
    request: InterviewGuideRequest
):
    """流式生成面试指导文档"""
    return StreamingResponse(
        interview_ai_service.stream_interview_guide_two_stage(db, request),
        media_type="text/event-stream"
    ) 