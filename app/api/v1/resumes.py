from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from uuid import UUID

from app.database import get_db
from app.models import Resume
from app.schemas.resume import ResumeResponse, ResumeExtractedData
from app.schemas.match import MatchResponse
from app.utils.file_handler import file_handler
from app.services.resume_parser import resume_parser
from app.services.nlp_extractor import nlp_extractor
from app.services.embedding_service import get_embedding_service
from app.services.vector_store import get_vector_store
from app.services.matching_service import get_matching_service
from app.config import settings

router = APIRouter()


@router.post("/upload", response_model=dict)
async def upload_resume(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload a resume PDF file.

    - Extracts text from PDF
    - Uses NLP to extract skills, education, experience
    - Generates embeddings for matching
    - Stores in database and vector store
    """
    # Validate file
    is_valid, error = file_handler.validate_file(file)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error)

    try:
        # Save file
        saved_filename, file_path = await file_handler.save_file(file)

        # Parse PDF
        raw_text = resume_parser.parse(file_path)

        # Extract information using NLP
        extracted = nlp_extractor.extract(raw_text)

        # Create resume record
        resume = Resume(
            filename=file.filename,
            file_path=file_path,
            raw_text=raw_text,
            name=extracted.name,
            email=extracted.email,
            phone=extracted.phone,
            skills=extracted.skills,
            education=[vars(e) if hasattr(e, '__dict__') else e for e in extracted.education],
            experience=[vars(e) if hasattr(e, '__dict__') else e for e in extracted.experience]
        )

        db.add(resume)
        await db.flush()

        # Generate and store embedding
        embedding_service = get_embedding_service()
        embedding_text = embedding_service.create_resume_embedding_text(
            skills=extracted.skills,
            experience=extracted.experience,
            education=extracted.education
        )
        embedding = embedding_service.generate_embedding(embedding_text)

        # Store in vector database
        vector_store = get_vector_store()
        vector_store.add_resume(
            resume_id=str(resume.id),
            embedding=embedding,
            metadata={
                "name": extracted.name,
                "skills": ", ".join(extracted.skills) if extracted.skills else ""
            }
        )

        resume.embedding_id = str(resume.id)
        await db.commit()

        return {
            "id": resume.id,
            "filename": file.filename,
            "message": "Resume uploaded and processed successfully",
            "extracted_data": {
                "name": extracted.name,
                "email": extracted.email,
                "phone": extracted.phone,
                "skills": extracted.skills,
                "education": extracted.education,
                "experience": extracted.experience
            }
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing resume: {str(e)}")


@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(
    resume_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get resume details by ID."""
    resume = await db.get(Resume, resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    return resume


@router.get("/{resume_id}/matches", response_model=List[MatchResponse])
async def get_resume_matches(
    resume_id: UUID,
    limit: int = Query(default=10, ge=1, le=50),
    min_score: float = Query(default=None, ge=0, le=1),
    db: AsyncSession = Depends(get_db)
):
    """
    Get matching jobs for a resume.

    - Uses vector similarity to find best matching jobs
    - Returns jobs sorted by match score
    """
    try:
        matching_service = get_matching_service()
        matches = await matching_service.get_matching_jobs_for_resume(
            db=db,
            resume_id=resume_id,
            limit=limit,
            min_score=min_score or settings.match_threshold
        )
        return matches
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/", response_model=List[ResumeResponse])
async def list_resumes(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """List all resumes with pagination."""
    result = await db.execute(
        select(Resume)
        .order_by(Resume.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


@router.delete("/{resume_id}")
async def delete_resume(
    resume_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Delete a resume."""
    resume = await db.get(Resume, resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    # Delete from vector store
    vector_store = get_vector_store()
    vector_store.delete_resume(str(resume_id))

    # Delete file
    file_handler.delete_file(resume.file_path)

    # Delete from database
    await db.delete(resume)
    await db.commit()

    return {"message": "Resume deleted successfully"}
