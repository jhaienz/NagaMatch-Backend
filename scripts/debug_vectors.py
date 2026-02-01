#!/usr/bin/env python3
"""
Debug script to check vector store contents and test matching.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.vector_store import get_vector_store
from app.services.embedding_service import get_embedding_service

def main():
    print("=" * 50)
    print("NagaMatch Vector Store Debug")
    print("=" * 50)
    print()

    vector_store = get_vector_store()

    # Check resumes
    print(f"Resumes in vector store: {len(vector_store.resumes)}")
    for resume_id, data in vector_store.resumes.items():
        print(f"  - {resume_id}: {data.get('metadata', {})}")

    print()

    # Check jobs
    print(f"Jobs in vector store: {len(vector_store.jobs)}")
    for job_id, data in vector_store.jobs.items():
        print(f"  - {job_id}: {data.get('metadata', {})}")

    print()

    # Test matching if we have both
    if vector_store.resumes and vector_store.jobs:
        print("Testing matching...")
        print()

        # Get first resume embedding
        first_resume_id = list(vector_store.resumes.keys())[0]
        resume_embedding = vector_store.resumes[first_resume_id]["embedding"]

        print(f"Finding matches for resume: {first_resume_id}")
        print()

        # Find matches with no threshold
        matches = vector_store.find_matching_jobs(
            resume_embedding=resume_embedding,
            limit=10,
            min_score=0.0
        )

        print(f"Found {len(matches)} matches:")
        for match in matches:
            print(f"  - Job {match['job_id']}: score={match['score']:.4f}")
            print(f"    Metadata: {match.get('metadata', {})}")

        print()
        print("Score interpretation:")
        print("  0.9+ = Excellent match")
        print("  0.8+ = Good match")
        print("  0.7+ = Decent match")
        print("  0.6+ = Possible match")
        print("  <0.6 = Weak match")
    else:
        if not vector_store.resumes:
            print("No resumes in vector store! Upload resumes first.")
        if not vector_store.jobs:
            print("No jobs in vector store! Create jobs first.")

    print()
    print("=" * 50)


if __name__ == "__main__":
    main()
