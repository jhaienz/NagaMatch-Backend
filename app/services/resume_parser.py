import pdfplumber
from typing import Optional
import re


class ResumeParser:
    """Service for extracting text from PDF resumes."""

    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        """
        Extract all text from a PDF file.

        Args:
            file_path: Path to the PDF file

        Returns:
            Extracted text as a single string
        """
        text_content = []

        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    # Extract text with layout preservation
                    page_text = page.extract_text(
                        x_tolerance=3,
                        y_tolerance=3,
                        layout=False
                    )
                    if page_text:
                        text_content.append(page_text)
        except Exception as e:
            raise ValueError(f"Failed to extract text from PDF: {str(e)}")

        return "\n\n".join(text_content)

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean and normalize extracted text while preserving structure.

        Args:
            text: Raw extracted text

        Returns:
            Cleaned text with preserved line breaks
        """
        # Normalize line endings
        text = text.replace('\r\n', '\n').replace('\r', '\n')

        # Replace multiple spaces (but not newlines) with single space
        text = re.sub(r'[^\S\n]+', ' ', text)

        # Remove excessive blank lines (more than 2 consecutive)
        text = re.sub(r'\n{3,}', '\n\n', text)

        # Clean up lines - strip each line
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(lines)

        # Remove empty lines at start/end
        text = text.strip()

        return text

    def parse(self, file_path: str) -> str:
        """
        Parse a PDF resume and return cleaned text.

        Args:
            file_path: Path to the PDF file

        Returns:
            Cleaned extracted text
        """
        raw_text = self.extract_text_from_pdf(file_path)
        return self.clean_text(raw_text)


# Singleton instance
resume_parser = ResumeParser()
