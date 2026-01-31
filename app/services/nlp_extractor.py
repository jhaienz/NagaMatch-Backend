import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


# Comprehensive skills database for all types of jobs
SKILLS_DATABASE = {
    # Food & Culinary
    "cooking", "baking", "grilling", "food preparation", "food handling",
    "kitchen management", "menu planning", "catering", "bartending", "barista",
    "food safety", "culinary arts", "pastry", "butchering", "sushi making",
    "food plating", "recipe development", "inventory management",

    # Restaurant & Hospitality
    "customer service", "cashier", "point of sale", "pos system", "waitstaff",
    "table service", "hosting", "reservation management", "hotel management",
    "front desk", "housekeeping", "room service", "concierge", "event planning",
    "banquet service", "food service", "fast food", "fine dining",

    # Retail & Sales
    "sales", "retail", "merchandising", "stock management", "inventory",
    "visual merchandising", "product display", "cash handling", "upselling",
    "customer relations", "store management", "loss prevention", "pricing",

    # Construction & Trades
    "carpentry", "plumbing", "electrical", "welding", "masonry", "roofing",
    "painting", "plastering", "tiling", "flooring", "concrete work",
    "blueprint reading", "construction", "renovation", "demolition",
    "scaffolding", "heavy equipment", "forklift", "crane operation",
    "hvac", "air conditioning", "refrigeration",

    # Automotive & Mechanical
    "auto repair", "mechanic", "automotive", "engine repair", "brake repair",
    "oil change", "tire service", "vehicle maintenance", "diesel mechanic",
    "motorcycle repair", "auto body", "auto painting", "car wash",

    # Beauty & Personal Care
    "hairstyling", "hair cutting", "hair coloring", "barbering", "makeup",
    "nail art", "manicure", "pedicure", "facial", "skin care", "massage",
    "spa services", "waxing", "threading", "beauty consultation",

    # Healthcare & Medical
    "nursing", "patient care", "first aid", "cpr", "vital signs",
    "medication administration", "phlebotomy", "caregiving", "elderly care",
    "childcare", "midwifery", "physical therapy", "dental assistant",
    "medical records", "healthcare", "home care", "rehabilitation",

    # Cleaning & Maintenance
    "cleaning", "janitorial", "sanitation", "disinfection", "laundry",
    "ironing", "housekeeping", "window cleaning", "carpet cleaning",
    "pressure washing", "grounds maintenance", "landscaping", "gardening",
    "lawn care", "tree trimming", "pest control",

    # Security & Safety
    "security", "guard", "surveillance", "cctv monitoring", "access control",
    "patrol", "emergency response", "crowd control", "loss prevention",
    "fire safety", "safety inspection", "security clearance",

    # Transportation & Delivery
    "driving", "delivery", "motorcycle delivery", "truck driving",
    "forklift operation", "logistics", "route planning", "dispatching",
    "warehouse", "shipping", "receiving", "packing", "loading",
    "courier", "freight handling", "supply chain",

    # Office & Administrative
    "typing", "data entry", "filing", "scheduling", "receptionist",
    "phone handling", "email management", "calendar management",
    "office management", "administrative support", "bookkeeping",
    "accounting", "payroll", "invoicing", "microsoft office", "excel",
    "word processing", "spreadsheets", "presentations",

    # Writing & Communication
    "writing", "editing", "proofreading", "journalism", "reporting",
    "content writing", "copywriting", "blogging", "social media",
    "public relations", "press release", "creative writing", "translation",
    "transcription", "technical writing", "documentation",

    # Arts & Creative
    "drawing", "illustration", "graphic design", "photography",
    "videography", "video editing", "photo editing", "animation",
    "crafts", "sewing", "embroidery", "pottery", "sculpture", "calligraphy",
    "interior design", "fashion design", "jewelry making", "woodworking",

    # Education & Training
    "teaching", "tutoring", "lesson planning", "classroom management",
    "curriculum development", "student assessment", "special education",
    "early childhood education", "adult education", "training", "coaching",
    "mentoring", "public speaking", "presentation skills",

    # Agriculture & Farming
    "farming", "planting", "harvesting", "irrigation", "crop management",
    "livestock", "poultry", "fishing", "aquaculture", "organic farming",
    "pesticide application", "farm equipment", "agricultural",

    # Manufacturing & Production
    "assembly", "machine operation", "quality control", "quality assurance",
    "production line", "packaging", "labeling", "inspection", "soldering",
    "sewing machine", "printing", "binding", "laminating",

    # Technology & IT
    "computer", "internet", "troubleshooting", "technical support", "networking",
    "computer repair", "software installation", "hardware installation",
    "python", "java", "javascript", "programming", "coding", "web development",
    "mobile development", "database", "sql", "excel", "powerpoint",
    "react", "node.js", "django", "flask", "docker", "aws", "git",
    "html", "css", "typescript", "mongodb", "postgresql", "api",

    # Finance & Accounting
    "accounting", "bookkeeping", "budgeting", "financial reporting",
    "tax preparation", "auditing", "billing", "collections", "credit analysis",
    "cash management", "payroll processing", "accounts payable",
    "accounts receivable", "quickbooks", "financial analysis",

    # Legal & Government
    "legal research", "document preparation", "notary", "court filing",
    "legal transcription", "paralegal", "compliance", "regulatory",

    # Soft Skills
    "communication", "teamwork", "leadership", "problem solving",
    "time management", "organization", "multitasking", "attention to detail",
    "critical thinking", "decision making", "adaptability", "flexibility",
    "work ethic", "reliability", "punctuality", "initiative", "creativity",
    "negotiation", "conflict resolution", "stress management", "agile",

    # Languages
    "english", "filipino", "tagalog", "bicol", "cebuano", "ilocano",
    "mandarin", "japanese", "korean", "spanish", "bilingual", "multilingual"
}

# Education keywords - expanded
EDUCATION_KEYWORDS = [
    "bachelor", "master", "phd", "doctorate", "associate", "degree", "diploma",
    "b.s.", "b.a.", "m.s.", "m.a.", "mba", "bscs", "bsit", "bsis", "bsba",
    "bsed", "beed", "bsn", "bs ", "ba ", "ms ", "ma ",
    "certificate", "certification", "vocational", "technical", "tesda",
    "nc i", "nc ii", "nc iii", "nc iv", "national certificate",
    "high school", "senior high", "junior high", "secondary",
    "elementary", "primary", "grade school",
    "graduate", "undergraduate", "college", "university"
]

# Section markers
SECTION_MARKERS = [
    "experience", "education", "skills", "summary", "objective",
    "profile", "work history", "employment", "qualifications",
    "certifications", "projects", "references", "contact"
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
        pass

    def _split_into_lines(self, text: str) -> List[str]:
        """Split text into lines, handling both newline-separated and continuous text."""
        # First try normal newline split
        lines = text.split('\n')

        # If we only got 1-2 lines, the PDF might not have preserved newlines
        # Try to split on common section headers
        if len(lines) <= 2 and len(text) > 200:
            # Insert newlines before common section headers
            for marker in SECTION_MARKERS:
                # Case insensitive replacement
                pattern = re.compile(r'\s+(' + re.escape(marker) + r')\s+', re.IGNORECASE)
                text = pattern.sub(r'\n\1\n', text)

            # Also split on patterns like "Phone", "Email", "Location"
            text = re.sub(r'\s+(Phone|Email|Location|Address|LinkedIn|Mobile)\s*', r'\n\1 ', text, flags=re.IGNORECASE)

            lines = text.split('\n')

        return [line.strip() for line in lines if line.strip()]

    def extract_email(self, text: str) -> Optional[str]:
        """Extract email address from text."""
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        matches = re.findall(email_pattern, text)
        return matches[0] if matches else None

    def extract_phone(self, text: str) -> Optional[str]:
        """Extract phone number from text."""
        phone_patterns = [
            r'09\d{9}',  # Philippines mobile: 09XXXXXXXXX
            r'\+63\s*\d{10}',  # Philippines with country code
            r'\+63\s*\d{3}\s*\d{3}\s*\d{4}',  # +63 XXX XXX XXXX
            r'\d{3}[-.\s]\d{3}[-.\s]\d{4}',  # XXX-XXX-XXXX or XXX.XXX.XXXX
            r'\(\d{3}\)\s*\d{3}[-.\s]?\d{4}',  # (XXX) XXX-XXXX
        ]

        for pattern in phone_patterns:
            matches = re.findall(pattern, text)
            if matches:
                return matches[0].strip()
        return None

    def extract_name(self, text: str) -> Optional[str]:
        """Extract person name from text using multiple strategies."""

        # Strategy 1: Look for name before "Phone" or "Email" keywords
        # Pattern like "ALEX R. DEVELOPER Phone..." or "John Doe Email:"
        name_before_contact = re.search(
            r'^([A-Z][A-Za-z]+(?:\s+[A-Z]\.?\s*)?(?:\s+[A-Z][A-Za-z]+)+)\s*(?:Phone|Email|Mobile|Contact|Address|\|)',
            text,
            re.MULTILINE
        )
        if name_before_contact:
            name = name_before_contact.group(1).strip()
            if 2 <= len(name.split()) <= 5:
                return name

        # Strategy 2: Look for all-caps name at the start
        all_caps_name = re.search(r'^([A-Z][A-Z\s.]+[A-Z])\s', text)
        if all_caps_name:
            name = all_caps_name.group(1).strip()
            words = name.split()
            if 2 <= len(words) <= 5 and not any(w.lower() in SECTION_MARKERS for w in words):
                return name

        # Strategy 3: Check first few lines
        lines = self._split_into_lines(text)

        skip_words = [
            'resume', 'cv', 'curriculum', 'vitae', 'profile', 'contact',
            'phone', 'address', 'summary', 'objective', 'experience',
            'education', 'skills', 'reference', 'personal', 'information',
            'email', 'mobile', 'linkedin', 'github'
        ]

        for line in lines[:10]:
            line = line.strip()
            if not line or len(line) < 3 or len(line) > 50:
                continue

            line_lower = line.lower()

            # Skip if contains contact info or section headers
            if any(kw in line_lower for kw in skip_words):
                continue
            if '@' in line or re.search(r'\d{3,}', line):
                continue

            # Check if it looks like a name
            words = line.split()
            if not (2 <= len(words) <= 5):
                continue

            # All words should start with capital letter
            valid_name = all(
                word[0].isupper() or word[0].isalpha() == False
                for word in words if word
            )

            if valid_name:
                return line

        return None

    def extract_skills(self, text: str) -> List[str]:
        """Extract skills from text using keyword matching."""
        text_lower = text.lower()
        found_skills = set()

        for skill in SKILLS_DATABASE:
            if ' ' in skill:
                if skill in text_lower:
                    found_skills.add(skill.title())
            else:
                pattern = r'\b' + re.escape(skill) + r'\b'
                if re.search(pattern, text_lower):
                    if len(skill) <= 3 and skill.isalpha():
                        found_skills.add(skill.upper())
                    else:
                        found_skills.add(skill.title())

        return sorted(list(found_skills))

    def extract_education(self, text: str) -> List[Dict[str, Any]]:
        """Extract education information from text."""
        education_list = []
        lines = self._split_into_lines(text)

        # Find education section
        in_education = False
        education_text = []

        for i, line in enumerate(lines):
            line_lower = line.lower()

            # Check if entering education section
            if 'education' in line_lower and len(line) < 50:
                in_education = True
                continue

            # Check if leaving education section
            if in_education:
                if any(marker in line_lower for marker in ['experience', 'skills', 'projects', 'references', 'certifications']):
                    if len(line) < 50:  # It's a header, not content
                        break

                education_text.append(line)

        # If no education section found, search whole text
        if not education_text:
            education_text = lines

        # Parse education entries
        for line in education_text:
            line_lower = line.lower()

            # Check for degree/education keywords
            has_edu_keyword = any(kw in line_lower for kw in EDUCATION_KEYWORDS)

            if has_edu_keyword:
                # Extract year if present
                year_match = re.search(r'(19|20)\d{2}', line)
                entry = {"degree": line}
                if year_match:
                    entry["year"] = year_match.group()
                education_list.append(entry)

        return education_list

    def extract_experience(self, text: str) -> List[Dict[str, Any]]:
        """Extract work experience information from text."""
        experience_list = []
        lines = self._split_into_lines(text)

        # Find experience section
        in_experience = False
        experience_text = []

        for line in lines:
            line_lower = line.lower()

            # Check if entering experience section
            if any(kw in line_lower for kw in ['experience', 'employment', 'work history']):
                if len(line) < 50:  # It's a header
                    in_experience = True
                    continue

            # Check if leaving experience section
            if in_experience:
                if any(marker in line_lower for marker in ['education', 'skills', 'projects', 'references']):
                    if len(line) < 50:
                        break

                experience_text.append(line)

        # If no experience section found, search for date patterns
        if not experience_text:
            experience_text = lines

        # Parse experience entries - look for date patterns
        date_pattern = r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s*\d{4}|(?:19|20)\d{2})\s*[-–—to]+\s*((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s*\d{4}|(?:19|20)\d{2}|[Pp]resent|[Cc]urrent)'

        current_entry = None

        for line in experience_text:
            # Check if line contains date range
            date_match = re.search(date_pattern, line)

            if date_match:
                if current_entry:
                    experience_list.append(current_entry)
                current_entry = {
                    "title": line,
                    "dates": date_match.group()
                }
            elif current_entry and len(line) > 10:
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
