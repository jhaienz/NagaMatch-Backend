from typing import List, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Resume, Job
from app.services.embedding_service import get_embedding_service
from app.services.vector_store import get_vector_store
from app.config import settings


class MatchingService:
    """Service for matching resumes to jobs using vector similarity."""

    def __init__(self):
        self.embedding_service = get_embedding_service()
        self.vector_store = get_vector_store()

    async def get_matching_jobs_for_resume(
        self,
        db: AsyncSession,
        resume_id: UUID,
        limit: int = None,
        min_score: float = None
    ) -> List[Dict[str, Any]]:
        """
        Find matching jobs for a resume.

        Args:
            db: Database session
            resume_id: Resume UUID
            limit: Maximum number of matches
            min_score: Minimum similarity score

        Returns:
            List of matching jobs with scores
        """
        limit = limit or settings.max_matches
        min_score = min_score or settings.match_threshold

        # Get resume from database
        resume = await db.get(Resume, resume_id)
        if not resume:
            raise ValueError(f"Resume {resume_id} not found")

        # Get resume embedding from vector store
        embedding = self.vector_store.get_resume_embedding(str(resume_id))
        if not embedding:
            # Generate embedding if not stored
            embedding_text = self.embedding_service.create_resume_embedding_text(
                skills=resume.skills or [],
                experience=resume.experience or [],
                education=resume.education or []
            )
            embedding = self.embedding_service.generate_embedding(embedding_text)

        # Find matching jobs in vector store
        matches = self.vector_store.find_matching_jobs(
            resume_embedding=embedding,
            limit=limit,
            min_score=min_score
        )

        # Enrich with job details from database
        enriched_matches = []
        for match in matches:
            job_id = UUID(match["job_id"])
            job = await db.get(Job, job_id)
            if job and job.is_active:
                enriched_matches.append({
                    "job_id": job_id,
                    "job_title": job.title,
                    "company": job.company,
                    "location": job.location,
                    "salary_min": job.salary_min,
                    "salary_max": job.salary_max,
                    "match_score": round(match["score"], 4)
                })

        # Sort by score descending
        enriched_matches.sort(key=lambda x: x["match_score"], reverse=True)

        return enriched_matches

    async def get_matching_resumes_for_job(
        self,
        db: AsyncSession,
        job_id: UUID,
        limit: int = None,
        min_score: float = None
    ) -> List[Dict[str, Any]]:
        """
        Find matching resumes/candidates for a job.

        Args:
            db: Database session
            job_id: Job UUID
            limit: Maximum number of matches
            min_score: Minimum similarity score

        Returns:
            List of matching candidates with scores
        """
        limit = limit or settings.max_matches
        min_score = min_score or settings.match_threshold

        # Get job from database
        job = await db.get(Job, job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")

        # Get job embedding from vector store
        embedding = self.vector_store.get_job_embedding(str(job_id))
        if not embedding:
            # Generate embedding if not stored
            embedding_text = self.embedding_service.create_job_embedding_text(
                title=job.title,
                description=job.description,
                requirements=job.requirements or []
            )
            embedding = self.embedding_service.generate_embedding(embedding_text)

        # Find matching resumes in vector store
        matches = self.vector_store.find_matching_resumes(
            job_embedding=embedding,
            limit=limit,
            min_score=min_score
        )

        # Enrich with resume details from database
        enriched_matches = []
        for match in matches:
            resume_id = UUID(match["resume_id"])
            resume = await db.get(Resume, resume_id)
            if resume:
                enriched_matches.append({
                    "resume_id": resume_id,
                    "name": resume.name,
                    "email": resume.email,
                    "skills": resume.skills or [],
                    "match_score": round(match["score"], 4)
                })

        # Sort by score descending
        enriched_matches.sort(key=lambda x: x["match_score"], reverse=True)

        return enriched_matches

    async def calculate_match_score(
        self,
        db: AsyncSession,
        resume_id: UUID,
        job_id: UUID
    ) -> float:
        """
        Calculate the match score between a specific resume and job.

        Args:
            db: Database session
            resume_id: Resume UUID
            job_id: Job UUID

        Returns:
            Match score (0-1)
        """
        resume_embedding = self.vector_store.get_resume_embedding(str(resume_id))
        job_embedding = self.vector_store.get_job_embedding(str(job_id))

        if not resume_embedding or not job_embedding:
            # Fallback: regenerate embeddings
            resume = await db.get(Resume, resume_id)
            job = await db.get(Job, job_id)

            if not resume or not job:
                return 0.0

            if not resume_embedding:
                resume_text = self.embedding_service.create_resume_embedding_text(
                    skills=resume.skills or [],
                    experience=resume.experience or [],
                    education=resume.education or []
                )
                resume_embedding = self.embedding_service.generate_embedding(resume_text)

            if not job_embedding:
                job_text = self.embedding_service.create_job_embedding_text(
                    title=job.title,
                    description=job.description,
                    requirements=job.requirements or []
                )
                job_embedding = self.embedding_service.generate_embedding(job_text)

        return self.embedding_service.cosine_similarity(resume_embedding, job_embedding)


# Singleton instance (lazy loaded)
_matching_service = None


def get_matching_service() -> MatchingService:
    global _matching_service
    if _matching_service is None:
        _matching_service = MatchingService()
    return _matching_service
