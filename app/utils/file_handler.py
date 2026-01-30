import os
import uuid
import aiofiles
from fastapi import UploadFile
from typing import Tuple
from app.config import settings


class FileHandler:
    """Utility class for handling file uploads."""

    ALLOWED_EXTENSIONS = {'.pdf'}

    @staticmethod
    def get_upload_dir() -> str:
        """Get the upload directory path and ensure it exists."""
        upload_dir = settings.upload_dir
        os.makedirs(upload_dir, exist_ok=True)
        return upload_dir

    @staticmethod
    def validate_file(file: UploadFile) -> Tuple[bool, str]:
        """
        Validate uploaded file.

        Args:
            file: The uploaded file

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not file.filename:
            return False, "No filename provided"

        # Check extension
        _, ext = os.path.splitext(file.filename)
        if ext.lower() not in FileHandler.ALLOWED_EXTENSIONS:
            return False, f"Invalid file type. Allowed: {', '.join(FileHandler.ALLOWED_EXTENSIONS)}"

        # Check content type
        if file.content_type not in ['application/pdf']:
            return False, "Invalid content type. Only PDF files are allowed."

        return True, ""

    @staticmethod
    async def save_file(file: UploadFile) -> Tuple[str, str]:
        """
        Save uploaded file to disk.

        Args:
            file: The uploaded file

        Returns:
            Tuple of (saved_filename, file_path)
        """
        upload_dir = FileHandler.get_upload_dir()

        # Generate unique filename
        ext = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{ext}"
        file_path = os.path.join(upload_dir, unique_filename)

        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()

            # Check file size
            if len(content) > settings.max_upload_size:
                raise ValueError(
                    f"File too large. Maximum size: {settings.max_upload_size / 1024 / 1024}MB"
                )

            await f.write(content)

        return unique_filename, file_path

    @staticmethod
    def delete_file(file_path: str) -> bool:
        """
        Delete a file from disk.

        Args:
            file_path: Path to the file

        Returns:
            True if deleted, False otherwise
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
        except Exception:
            pass
        return False


file_handler = FileHandler()
