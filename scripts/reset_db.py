#!/usr/bin/env python3
"""
Database Reset Script for NagaMatch

WARNING: This script will DELETE ALL DATA in the database.
Only use for development/testing purposes.

Usage:
    python scripts/reset_db.py

Or make executable and run:
    chmod +x scripts/reset_db.py
    ./scripts/reset_db.py
"""

import asyncio
import sys
import os
import shutil

# Add parent directory to path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.database import engine, Base, async_session
from app.config import settings


async def reset_database():
    """Drop all tables and recreate them."""

    print("=" * 50)
    print("NagaMatch Database Reset Script")
    print("=" * 50)
    print()
    print("WARNING: This will DELETE ALL DATA!")
    print()

    # Confirm
    confirm = input("Type 'RESET' to confirm: ")
    if confirm != "RESET":
        print("Aborted.")
        return

    print()
    print("Resetting database...")

    # Drop all tables
    async with engine.begin() as conn:
        print("  - Dropping all tables...")
        await conn.run_sync(Base.metadata.drop_all)

        print("  - Creating all tables...")
        await conn.run_sync(Base.metadata.create_all)

    print("  - Database tables reset!")

    # Clear uploaded files
    upload_dir = settings.upload_dir
    if os.path.exists(upload_dir):
        for filename in os.listdir(upload_dir):
            if filename != '.gitkeep':
                filepath = os.path.join(upload_dir, filename)
                try:
                    os.remove(filepath)
                except Exception as e:
                    print(f"  - Warning: Could not delete {filepath}: {e}")
        print(f"  - Cleared uploads directory!")

    # Clear vector store data
    vector_dir = settings.chroma_persist_dir
    if os.path.exists(vector_dir):
        for filename in os.listdir(vector_dir):
            filepath = os.path.join(vector_dir, filename)
            try:
                if os.path.isfile(filepath):
                    os.remove(filepath)
                elif os.path.isdir(filepath):
                    shutil.rmtree(filepath)
            except Exception as e:
                print(f"  - Warning: Could not delete {filepath}: {e}")
        print(f"  - Cleared vector store directory!")

    print()
    print("=" * 50)
    print("Database reset complete!")
    print("=" * 50)


async def quick_reset():
    """Quick reset without confirmation (for scripting)."""
    print("Quick resetting database...")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # Clear files
    for directory in [settings.upload_dir, settings.chroma_persist_dir]:
        if os.path.exists(directory):
            for filename in os.listdir(directory):
                if filename != '.gitkeep':
                    filepath = os.path.join(directory, filename)
                    try:
                        if os.path.isfile(filepath):
                            os.remove(filepath)
                        elif os.path.isdir(filepath):
                            shutil.rmtree(filepath)
                    except:
                        pass

    print("Done!")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--force":
        asyncio.run(quick_reset())
    else:
        asyncio.run(reset_database())
