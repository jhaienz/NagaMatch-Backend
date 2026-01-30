from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from uuid import UUID

from app.database import get_db
from app.models import Job
from app.schemas.job import JobCreate, JobUpdate, JobResponse
from app.schemas.match import CandidateMatchResponse
from app.services.embedding_service import get_embedding_service
from app.services.vector_store import get_vector_store
from app.services.matching_service import get_matching_service
from app.config import settings

router = APIRouter()


@router.post("/", response_model=JobResponse)
async def create_job(
    job_data: JobCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new job posting.

    - Generates embedding for AI matching
    - Stores in database and vector store
    """
    # Create job record
    job = Job(
        title=job_data.title,
        company=job_data.company,
        description=job_data.description,
        requirements=job_data.requirements,
        location=job_data.location,
        salary_min=job_data.salary_min,
        salary_max=job_data.salary_max,
        job_type=job_data.job_type
    )

    db.add(job)
    await db.flush()

    # Generate and store embedding
    embedding_service = get_embedding_service()
    embedding_text = embedding_service.create_job_embedding_text(
        title=job_data.title,
        description=job_data.description,
        requirements=job_data.requirements
    )
    embedding = embedding_service.generate_embedding(embedding_text)

    # Store in vector database
    vector_store = get_vector_store()
    vector_store.add_job(
        job_id=str(job.id),
        embedding=embedding,
        metadata={
            "title": job_data.title,
            "company": job_data.company,
            "requirements": ", ".join(job_data.requirements) if job_data.requirements else ""
        }
    )

    job.embedding_id = str(job.id)
    await db.commit()

    return job


@router.get("/", response_model=List[JobResponse])
async def list_jobs(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    location: Optional[str] = None,
    is_active: bool = True,
    db: AsyncSession = Depends(get_db)
):
    """List all job postings with optional filters."""
    query = select(Job).where(Job.is_active == is_active)

    if location:
        query = query.where(Job.location.ilike(f"%{location}%"))

    query = query.order_by(Job.created_at.desc()).offset(skip).limit(limit)

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get job details by ID."""
    job = await db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.put("/{job_id}", response_model=JobResponse)
async def update_job(
    job_id: UUID,
    job_data: JobUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a job posting."""
    job = await db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Update fields
    update_data = job_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(job, field, value)

    # Regenerate embedding if content changed
    if any(key in update_data for key in ['title', 'description', 'requirements']):
        embedding_service = get_embedding_service()
        embedding_text = embedding_service.create_job_embedding_text(
            title=job.title,
            description=job.description,
            requirements=job.requirements or []
        )
        embedding = embedding_service.generate_embedding(embedding_text)

        vector_store = get_vector_store()
        vector_store.update_job(
            job_id=str(job_id),
            embedding=embedding,
            metadata={
                "title": job.title,
                "company": job.company,
                "requirements": ", ".join(job.requirements) if job.requirements else ""
            }
        )

    await db.commit()
    await db.refresh(job)
    return job


@router.delete("/{job_id}")
async def delete_job(
    job_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Delete a job posting."""
    job = await db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Delete from vector store
    vector_store = get_vector_store()
    vector_store.delete_job(str(job_id))

    # Delete from database
    await db.delete(job)
    await db.commit()

    return {"message": "Job deleted successfully"}


@router.get("/{job_id}/candidates", response_model=List[CandidateMatchResponse])
async def get_job_candidates(
    job_id: UUID,
    limit: int = Query(default=10, ge=1, le=50),
    min_score: float = Query(default=None, ge=0, le=1),
    db: AsyncSession = Depends(get_db)
):
    """
    Get matching candidates/resumes for a job.

    - Uses vector similarity to find best matching resumes
    - Returns candidates sorted by match score
    """
    try:
        matching_service = get_matching_service()
        matches = await matching_service.get_matching_resumes_for_job(
            db=db,
            job_id=job_id,
            limit=limit,
            min_score=min_score or settings.match_threshold
        )
        return matches
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
