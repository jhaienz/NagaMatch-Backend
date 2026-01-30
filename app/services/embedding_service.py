from sentence_transformers import SentenceTransformer
from typing import List, Union
import numpy as np
from app.config import settings


class EmbeddingService:
    """Service for generating text embeddings using sentence-transformers."""

    def __init__(self, model_name: str = None):
        """
        Initialize the embedding service.

        Args:
            model_name: Name of the sentence-transformer model to use
        """
        self.model_name = model_name or settings.embedding_model
        self.model = SentenceTransformer(self.model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            Embedding as list of floats
        """
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed

        Returns:
            List of embeddings
        """
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()

    def create_resume_embedding_text(
        self,
        skills: List[str],
        experience: List[dict],
        education: List[dict]
    ) -> str:
        """
        Create a combined text representation of resume for embedding.

        Args:
            skills: List of skills
            experience: List of experience dictionaries
            education: List of education dictionaries

        Returns:
            Combined text for embedding
        """
        parts = []

        # Add skills
        if skills:
            parts.append(f"Skills: {', '.join(skills)}")

        # Add experience
        for exp in experience:
            exp_text = []
            if exp.get("title"):
                exp_text.append(exp["title"])
            if exp.get("company"):
                exp_text.append(f"at {exp['company']}")
            if exp.get("description"):
                exp_text.append(exp["description"])
            if exp_text:
                parts.append(" ".join(exp_text))

        # Add education
        for edu in education:
            edu_text = []
            if edu.get("degree"):
                edu_text.append(edu["degree"])
            if edu.get("institution"):
                edu_text.append(f"from {edu['institution']}")
            if edu.get("field"):
                edu_text.append(f"in {edu['field']}")
            if edu_text:
                parts.append(" ".join(edu_text))

        return " | ".join(parts) if parts else ""

    def create_job_embedding_text(
        self,
        title: str,
        description: str,
        requirements: List[str]
    ) -> str:
        """
        Create a combined text representation of job posting for embedding.

        Args:
            title: Job title
            description: Job description
            requirements: List of required skills

        Returns:
            Combined text for embedding
        """
        parts = [f"Job Title: {title}"]

        if requirements:
            parts.append(f"Required Skills: {', '.join(requirements)}")

        if description:
            # Limit description length for embedding
            desc_truncated = description[:500]
            parts.append(f"Description: {desc_truncated}")

        return " | ".join(parts)

    @staticmethod
    def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors.

        Args:
            vec1: First vector
            vec2: Second vector

        Returns:
            Cosine similarity score (0-1)
        """
        a = np.array(vec1)
        b = np.array(vec2)

        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return float(dot_product / (norm_a * norm_b))


# Singleton instance (lazy loaded to avoid loading model on import)
_embedding_service = None


def get_embedding_service() -> EmbeddingService:
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
