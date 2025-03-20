from pydantic import BaseModel
from typing import Optional
from datetime import date


class TalentCertificationBase(BaseModel):
    certification_name: str
    issuing_organization: Optional[str]
    issue_date: Optional[date]
    expiration_date: Optional[date]
    document_url: Optional[str]


class TalentCertificationCreate(TalentCertificationBase):
    talent_id: int


class TalentCertificationUpdate(TalentCertificationBase):
    pass


class TalentCertificationResponse(TalentCertificationBase):
    certification_id: int
    talent_id: int

    class Config:
        from_attributes = True 