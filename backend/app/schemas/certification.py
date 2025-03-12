from pydantic import BaseModel
from typing import Optional
from datetime import date


class CertificationBase(BaseModel):
    certification_name: str
    issuing_organization: Optional[str]
    issue_date: Optional[date]
    expiration_date: Optional[date]
    document_url: Optional[str]


class CertificationCreate(CertificationBase):
    talent_id: int


class CertificationUpdate(CertificationBase):
    pass


class CertificationResponse(CertificationBase):
    certification_id: int
    talent_id: int

    class Config:
        orm_mode = True 