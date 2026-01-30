from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class MatchResponse(BaseModel):
    job_id: UUID
    job_title: str
    company: str
    match_score: float
    location: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None


class CandidateMatchResponse(BaseModel):
    resume_id: UUID
    name: Optional[str] = None
    email: Optional[str] = None
    skills: List[str] = []
    match_score: float


class ApplicationCreate(BaseModel):
    resume_id: UUID
    job_id: UUID


class ApplicationResponse(BaseModel):
    id: UUID
    resume_id: UUID
    job_id: UUID
    match_score: Optional[float] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class ApplicationWithDetails(BaseModel):
    id: UUID
    resume_id: UUID
    job_id: UUID
    job_title: str
    company: str
    match_score: Optional[float] = None
    status: str
    created_at: datetime
