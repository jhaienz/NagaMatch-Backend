from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class JobCreate(BaseModel):
    title: str
    company: str
    description: str
    requirements: List[str] = []
    location: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    job_type: Optional[str] = None


class JobUpdate(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[List[str]] = None
    location: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    job_type: Optional[str] = None
    is_active: Optional[bool] = None


class JobResponse(BaseModel):
    id: UUID
    title: str
    company: str
    description: str
    requirements: List[str] = []
    location: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    job_type: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
