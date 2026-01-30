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
                    page_text = page.extract_text()
                    if page_text:
                        text_content.append(page_text)
        except Exception as e:
            raise ValueError(f"Failed to extract text from PDF: {str(e)}")

        return "\n".join(text_content)

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean and normalize extracted text.

        Args:
            text: Raw extracted text

        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s@.,-]', '', text)

        return text.strip()

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
