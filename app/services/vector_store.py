import json
import os
import numpy as np
from typing import List, Dict, Any, Optional
from app.config import settings


class VectorStore:
    """Simple file-based vector store using NumPy for similarity search."""

    def __init__(self):
        """Initialize vector store with file persistence."""
        self.persist_dir = settings.chroma_persist_dir
        os.makedirs(self.persist_dir, exist_ok=True)

        self.resumes_file = os.path.join(self.persist_dir, "resumes.json")
        self.jobs_file = os.path.join(self.persist_dir, "jobs.json")

        self.resumes: Dict[str, Dict[str, Any]] = self._load_store(self.resumes_file)
        self.jobs: Dict[str, Dict[str, Any]] = self._load_store(self.jobs_file)

    def _load_store(self, filepath: str) -> Dict[str, Dict[str, Any]]:
        """Load vector store from file."""
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}

    def _save_store(self, data: Dict[str, Dict[str, Any]], filepath: str) -> None:
        """Save vector store to file."""
        with open(filepath, 'w') as f:
            json.dump(data, f)

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        a = np.array(vec1)
        b = np.array(vec2)

        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return float(dot_product / (norm_a * norm_b))

    def add_resume(
        self,
        resume_id: str,
        embedding: List[float],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Add a resume embedding to the vector store."""
        self.resumes[resume_id] = {
            "embedding": embedding,
            "metadata": metadata or {}
        }
        self._save_store(self.resumes, self.resumes_file)
        return resume_id

    def add_job(
        self,
        job_id: str,
        embedding: List[float],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Add a job posting embedding to the vector store."""
        self.jobs[job_id] = {
            "embedding": embedding,
            "metadata": metadata or {}
        }
        self._save_store(self.jobs, self.jobs_file)
        return job_id

    def find_matching_jobs(
        self,
        resume_embedding: List[float],
        limit: int = 10,
        min_score: float = 0.0
    ) -> List[Dict[str, Any]]:
        """Find jobs that match a resume embedding."""
        matches = []

        for job_id, job_data in self.jobs.items():
            similarity = self._cosine_similarity(resume_embedding, job_data["embedding"])

            if similarity >= min_score:
                matches.append({
                    "job_id": job_id,
                    "score": similarity,
                    "metadata": job_data.get("metadata", {})
                })

        # Sort by score descending
        matches.sort(key=lambda x: x["score"], reverse=True)

        return matches[:limit]

    def find_matching_resumes(
        self,
        job_embedding: List[float],
        limit: int = 10,
        min_score: float = 0.0
    ) -> List[Dict[str, Any]]:
        """Find resumes that match a job embedding."""
        matches = []

        for resume_id, resume_data in self.resumes.items():
            similarity = self._cosine_similarity(job_embedding, resume_data["embedding"])

            if similarity >= min_score:
                matches.append({
                    "resume_id": resume_id,
                    "score": similarity,
                    "metadata": resume_data.get("metadata", {})
                })

        # Sort by score descending
        matches.sort(key=lambda x: x["score"], reverse=True)

        return matches[:limit]

    def get_resume_embedding(self, resume_id: str) -> Optional[List[float]]:
        """Get embedding for a specific resume."""
        if resume_id in self.resumes:
            return self.resumes[resume_id]["embedding"]
        return None

    def get_job_embedding(self, job_id: str) -> Optional[List[float]]:
        """Get embedding for a specific job."""
        if job_id in self.jobs:
            return self.jobs[job_id]["embedding"]
        return None

    def delete_resume(self, resume_id: str) -> None:
        """Delete a resume embedding."""
        if resume_id in self.resumes:
            del self.resumes[resume_id]
            self._save_store(self.resumes, self.resumes_file)

    def delete_job(self, job_id: str) -> None:
        """Delete a job embedding."""
        if job_id in self.jobs:
            del self.jobs[job_id]
            self._save_store(self.jobs, self.jobs_file)

    def update_job(
        self,
        job_id: str,
        embedding: List[float],
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Update a job embedding."""
        self.jobs[job_id] = {
            "embedding": embedding,
            "metadata": metadata or {}
        }
        self._save_store(self.jobs, self.jobs_file)


# Singleton instance (lazy loaded)
_vector_store = None


def get_vector_store() -> VectorStore:
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store
