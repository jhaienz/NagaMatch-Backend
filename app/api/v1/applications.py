from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from uuid import UUID

from app.database import get_db
from app.models import Application, Resume, Job
from app.schemas.match import ApplicationCreate, ApplicationResponse, ApplicationWithDetails
from app.services.matching_service import get_matching_service

router = APIRouter()


@router.post("/", response_model=ApplicationResponse)
async def create_application(
    application_data: ApplicationCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Submit a job application.

    - Links resume to job posting
    - Calculates and stores match score
    """
    # Verify resume exists
    resume = await db.get(Resume, application_data.resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    # Verify job exists and is active
    job = await db.get(Job, application_data.job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if not job.is_active:
        raise HTTPException(status_code=400, detail="Job is no longer accepting applications")

    # Check if already applied
    existing = await db.execute(
        select(Application).where(
            and_(
                Application.resume_id == application_data.resume_id,
                Application.job_id == application_data.job_id
            )
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Already applied to this job")

    # Calculate match score
    matching_service = get_matching_service()
    match_score = await matching_service.calculate_match_score(
        db=db,
        resume_id=application_data.resume_id,
        job_id=application_data.job_id
    )

    # Create application
    application = Application(
        resume_id=application_data.resume_id,
        job_id=application_data.job_id,
        match_score=round(match_score, 4),
        status="applied"
    )

    db.add(application)
    await db.commit()
    await db.refresh(application)

    return application


@router.get("/", response_model=List[ApplicationWithDetails])
async def list_applications(
    resume_id: Optional[UUID] = None,
    job_id: Optional[UUID] = None,
    status: Optional[str] = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    List applications with optional filters.

    - Filter by resume_id to see all applications for a person
    - Filter by job_id to see all applicants for a job
    - Filter by status to see applications in specific stage
    """
    query = select(Application)

    if resume_id:
        query = query.where(Application.resume_id == resume_id)
    if job_id:
        query = query.where(Application.job_id == job_id)
    if status:
        query = query.where(Application.status == status)

    query = query.order_by(Application.created_at.desc()).offset(skip).limit(limit)

    result = await db.execute(query)
    applications = result.scalars().all()

    # Enrich with job details
    enriched = []
    for app in applications:
        job = await db.get(Job, app.job_id)
        enriched.append(ApplicationWithDetails(
            id=app.id,
            resume_id=app.resume_id,
            job_id=app.job_id,
            job_title=job.title if job else "Unknown",
            company=job.company if job else "Unknown",
            match_score=app.match_score,
            status=app.status,
            created_at=app.created_at
        ))

    return enriched


@router.get("/{application_id}", response_model=ApplicationWithDetails)
async def get_application(
    application_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get application details by ID."""
    application = await db.get(Application, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    job = await db.get(Job, application.job_id)

    return ApplicationWithDetails(
        id=application.id,
        resume_id=application.resume_id,
        job_id=application.job_id,
        job_title=job.title if job else "Unknown",
        company=job.company if job else "Unknown",
        match_score=application.match_score,
        status=application.status,
        created_at=application.created_at
    )


@router.patch("/{application_id}/status")
async def update_application_status(
    application_id: UUID,
    status: str = Query(..., description="New status: applied, screening, interview, hired, rejected"),
    db: AsyncSession = Depends(get_db)
):
    """Update application status."""
    valid_statuses = ["applied", "screening", "interview", "hired", "rejected"]
    if status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )

    application = await db.get(Application, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    application.status = status
    await db.commit()

    return {"message": f"Application status updated to {status}"}


@router.delete("/{application_id}")
async def delete_application(
    application_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Delete/withdraw an application."""
    application = await db.get(Application, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    await db.delete(application)
    await db.commit()

    return {"message": "Application deleted successfully"}
