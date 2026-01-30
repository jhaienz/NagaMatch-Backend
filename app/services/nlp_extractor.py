import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


# Common technical skills database for matching
TECHNICAL_SKILLS = {
    # Programming Languages
    "python", "java", "javascript", "typescript", "c++", "c#", "ruby", "php",
    "swift", "kotlin", "go", "rust", "scala", "perl", "r", "matlab", "sql",

    # Web Technologies
    "html", "css", "react", "angular", "vue", "node.js", "express", "django",
    "flask", "fastapi", "spring", "laravel", "asp.net", "jquery", "bootstrap",
    "tailwind", "sass", "webpack", "nextjs", "nuxtjs",

    # Databases
    "mysql", "postgresql", "mongodb", "redis", "elasticsearch", "oracle",
    "sqlite", "cassandra", "dynamodb", "firebase", "mariadb",

    # Cloud & DevOps
    "aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "terraform",
    "ansible", "ci/cd", "git", "github", "gitlab", "bitbucket", "linux",

    # Data Science & AI
    "machine learning", "deep learning", "tensorflow", "pytorch", "keras",
    "pandas", "numpy", "scikit-learn", "nlp", "computer vision", "data analysis",
    "data visualization", "tableau", "power bi", "spark", "hadoop",

    # Mobile Development
    "android", "ios", "react native", "flutter", "xamarin", "ionic",

    # Other Skills
    "api", "rest", "graphql", "microservices", "agile", "scrum", "jira",
    "figma", "adobe", "photoshop", "illustrator", "ui/ux", "project management"
}

# Education keywords
EDUCATION_KEYWORDS = [
    "bachelor", "master", "phd", "doctorate", "associate", "degree", "diploma",
    "b.s.", "b.a.", "m.s.", "m.a.", "mba", "bscs", "bsit", "bsis"
]

# Experience keywords
EXPERIENCE_KEYWORDS = [
    "experience", "work history", "employment", "professional experience",
    "work experience", "career history"
]


@dataclass
class ExtractedData:
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    skills: List[str] = field(default_factory=list)
    education: List[Dict[str, Any]] = field(default_factory=list)
    experience: List[Dict[str, Any]] = field(default_factory=list)


class NLPExtractor:
    """Service for extracting structured information from resume text using regex patterns."""

    def __init__(self):
        # No external dependencies needed - pure Python regex
        pass

    def extract_email(self, text: str) -> Optional[str]:
        """Extract email address from text."""
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        matches = re.findall(email_pattern, text)
        return matches[0] if matches else None

    def extract_phone(self, text: str) -> Optional[str]:
        """Extract phone number from text."""
        phone_patterns = [
            r'\+?1?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            r'\d{4}[-.\s]?\d{3}[-.\s]?\d{4}',
            r'\(\d{3}\)\s*\d{3}[-.\s]?\d{4}',
            r'09\d{9}'  # Philippines mobile format
        ]

        for pattern in phone_patterns:
            matches = re.findall(pattern, text)
            if matches:
                return matches[0]
        return None

    def extract_name(self, text: str) -> Optional[str]:
        """Extract person name from text using heuristics."""
        lines = text.split('\n')

        # Try to get name from first few lines
        for line in lines[:5]:
            line = line.strip()
            if not line:
                continue

            # Skip common header words
            skip_words = ['resume', 'cv', 'curriculum', 'vitae', 'profile',
                         'contact', 'email', 'phone', 'address', 'summary']
            if any(kw in line.lower() for kw in skip_words):
                continue

            # Skip lines with email or phone
            if '@' in line or re.search(r'\d{3}[-.\s]?\d{3}', line):
                continue

            # Name is likely 2-4 words, no numbers
            words = line.split()
            if 1 <= len(words) <= 4 and not any(c.isdigit() for c in line):
                # Check if it looks like a name (starts with capital letters)
                if all(w[0].isupper() for w in words if w):
                    return line

        return None

    def extract_skills(self, text: str) -> List[str]:
        """Extract skills from text using keyword matching."""
        text_lower = text.lower()
        found_skills = []

        # Match against known skills database
        for skill in TECHNICAL_SKILLS:
            # Use word boundary matching
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                # Capitalize properly
                if len(skill) <= 3:
                    found_skills.append(skill.upper())
                elif skill in ['node.js', 'asp.net', 'ci/cd', 'ui/ux']:
                    found_skills.append(skill)
                else:
                    found_skills.append(skill.title())

        return list(set(found_skills))

    def extract_education(self, text: str) -> List[Dict[str, Any]]:
        """Extract education information from text."""
        education_list = []
        lines = text.split('\n')

        in_education_section = False
        education_lines = []

        for line in lines:
            line_lower = line.lower().strip()

            # Check if entering education section
            if any(kw in line_lower for kw in ['education', 'academic', 'qualification']):
                in_education_section = True
                continue

            # Check if leaving education section
            if in_education_section and any(kw in line_lower for kw in EXPERIENCE_KEYWORDS + ['skills', 'references']):
                break

            if in_education_section and line.strip():
                education_lines.append(line.strip())

        # Parse education entries
        current_entry = {}
        for line in education_lines:
            line_lower = line.lower()

            # Check for degree keywords
            if any(kw in line_lower for kw in EDUCATION_KEYWORDS):
                if current_entry:
                    education_list.append(current_entry)
                current_entry = {"degree": line}
            elif current_entry and not current_entry.get("institution"):
                current_entry["institution"] = line

        if current_entry:
            education_list.append(current_entry)

        return education_list

    def extract_experience(self, text: str) -> List[Dict[str, Any]]:
        """Extract work experience information from text."""
        experience_list = []
        lines = text.split('\n')

        in_experience_section = False
        experience_lines = []

        for line in lines:
            line_lower = line.lower().strip()

            # Check if entering experience section
            if any(kw in line_lower for kw in EXPERIENCE_KEYWORDS):
                in_experience_section = True
                continue

            # Check if leaving experience section
            if in_experience_section and any(kw in line_lower for kw in ['education', 'skills', 'references']):
                break

            if in_experience_section and line.strip():
                experience_lines.append(line.strip())

        # Parse experience entries
        date_pattern = r'\d{4}\s*[-–]\s*(\d{4}|present|current)'
        current_entry = {}

        for line in experience_lines:
            # Check if line contains date range (likely new position)
            if re.search(date_pattern, line.lower()):
                if current_entry:
                    experience_list.append(current_entry)
                current_entry = {"title": line}
            elif current_entry:
                if not current_entry.get("company"):
                    current_entry["company"] = line
                elif not current_entry.get("description"):
                    current_entry["description"] = line

        if current_entry:
            experience_list.append(current_entry)

        return experience_list

    def extract(self, text: str) -> ExtractedData:
        """
        Extract all structured information from resume text.

        Args:
            text: Raw resume text

        Returns:
            ExtractedData with all extracted fields
        """
        return ExtractedData(
            name=self.extract_name(text),
            email=self.extract_email(text),
            phone=self.extract_phone(text),
            skills=self.extract_skills(text),
            education=self.extract_education(text),
            experience=self.extract_experience(text)
        )


# Singleton instance
nlp_extractor = NLPExtractor()
