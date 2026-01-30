# NagaMatch API Documentation

**Base URL**: `http://localhost:8000`

**Interactive Docs**:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Overview

NagaMatch is an AI-powered employment matching platform that:
1. Extracts skills, education, and experience from PDF resumes
2. Matches job seekers to relevant job opportunities using vector similarity
3. Tracks job applications through the hiring pipeline

---

## Authentication

Currently, no authentication is required (MVP version).

---

## Endpoints

### Health & Info

#### `GET /`
Returns API information.

**Response:**
```json
{
  "name": "NagaMatch API",
  "version": "1.0.0",
  "description": "AI-powered employment matching platform",
  "docs": "/docs",
  "health": "/health"
}
```

#### `GET /health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

---

### Resumes

#### `POST /api/v1/resumes/upload`
Upload a PDF resume for processing.

**Request:**
- Content-Type: `multipart/form-data`
- Body: `file` (PDF file)

**Response:**
```json
{
  "id": "uuid",
  "filename": "resume.pdf",
  "message": "Resume uploaded and processed successfully",
  "extracted_data": {
    "name": "Juan Dela Cruz",
    "email": "juan@example.com",
    "phone": "09123456789",
    "skills": ["Python", "JavaScript", "React", "SQL"],
    "education": [
      {
        "degree": "Bachelor of Science in Computer Science",
        "institution": "University of the Philippines"
      }
    ],
    "experience": [
      {
        "title": "Software Developer",
        "company": "Tech Corp",
        "description": "Developed web applications"
      }
    ]
  }
}
```

---

#### `GET /api/v1/resumes`
List all resumes.

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `skip` | int | 0 | Number of records to skip |
| `limit` | int | 20 | Maximum records to return (max: 100) |

**Response:**
```json
[
  {
    "id": "uuid",
    "filename": "resume.pdf",
    "name": "Juan Dela Cruz",
    "email": "juan@example.com",
    "phone": "09123456789",
    "skills": ["Python", "JavaScript"],
    "education": [],
    "experience": [],
    "created_at": "2024-01-30T10:00:00"
  }
]
```

---

#### `GET /api/v1/resumes/{resume_id}`
Get resume details by ID.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `resume_id` | UUID | Resume ID |

**Response:**
```json
{
  "id": "uuid",
  "filename": "resume.pdf",
  "name": "Juan Dela Cruz",
  "email": "juan@example.com",
  "phone": "09123456789",
  "skills": ["Python", "JavaScript", "React"],
  "education": [],
  "experience": [],
  "created_at": "2024-01-30T10:00:00"
}
```

---

#### `GET /api/v1/resumes/{resume_id}/matches`
Get matching jobs for a resume using AI similarity.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `resume_id` | UUID | Resume ID |

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | int | 10 | Maximum matches to return (max: 50) |
| `min_score` | float | 0.75 | Minimum similarity score (0-1) |

**Response:**
```json
[
  {
    "job_id": "uuid",
    "job_title": "Python Developer",
    "company": "Tech Corp",
    "match_score": 0.89,
    "location": "Naga City",
    "salary_min": 25000,
    "salary_max": 40000
  }
]
```

---

#### `DELETE /api/v1/resumes/{resume_id}`
Delete a resume.

**Response:**
```json
{
  "message": "Resume deleted successfully"
}
```

---

### Jobs

#### `POST /api/v1/jobs`
Create a new job posting.

**Request Body:**
```json
{
  "title": "Python Developer",
  "company": "Tech Corp",
  "description": "We are looking for an experienced Python developer...",
  "requirements": ["Python", "FastAPI", "PostgreSQL", "Docker"],
  "location": "Naga City",
  "salary_min": 25000,
  "salary_max": 40000,
  "job_type": "full-time"
}
```

**Response:**
```json
{
  "id": "uuid",
  "title": "Python Developer",
  "company": "Tech Corp",
  "description": "We are looking for an experienced Python developer...",
  "requirements": ["Python", "FastAPI", "PostgreSQL", "Docker"],
  "location": "Naga City",
  "salary_min": 25000,
  "salary_max": 40000,
  "job_type": "full-time",
  "is_active": true,
  "created_at": "2024-01-30T10:00:00"
}
```

---

#### `GET /api/v1/jobs`
List all job postings.

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `skip` | int | 0 | Number of records to skip |
| `limit` | int | 20 | Maximum records to return (max: 100) |
| `location` | string | null | Filter by location |
| `is_active` | bool | true | Filter by active status |

**Response:**
```json
[
  {
    "id": "uuid",
    "title": "Python Developer",
    "company": "Tech Corp",
    "description": "...",
    "requirements": ["Python", "FastAPI"],
    "location": "Naga City",
    "salary_min": 25000,
    "salary_max": 40000,
    "job_type": "full-time",
    "is_active": true,
    "created_at": "2024-01-30T10:00:00"
  }
]
```

---

#### `GET /api/v1/jobs/{job_id}`
Get job details by ID.

**Response:**
```json
{
  "id": "uuid",
  "title": "Python Developer",
  "company": "Tech Corp",
  "description": "...",
  "requirements": ["Python", "FastAPI"],
  "location": "Naga City",
  "salary_min": 25000,
  "salary_max": 40000,
  "job_type": "full-time",
  "is_active": true,
  "created_at": "2024-01-30T10:00:00"
}
```

---

#### `PUT /api/v1/jobs/{job_id}`
Update a job posting.

**Request Body:** (all fields optional)
```json
{
  "title": "Senior Python Developer",
  "salary_max": 50000,
  "is_active": false
}
```

---

#### `DELETE /api/v1/jobs/{job_id}`
Delete a job posting.

**Response:**
```json
{
  "message": "Job deleted successfully"
}
```

---

#### `GET /api/v1/jobs/{job_id}/candidates`
Get matching candidates/resumes for a job using AI similarity.

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | int | 10 | Maximum matches to return (max: 50) |
| `min_score` | float | 0.75 | Minimum similarity score (0-1) |

**Response:**
```json
[
  {
    "resume_id": "uuid",
    "name": "Juan Dela Cruz",
    "email": "juan@example.com",
    "skills": ["Python", "FastAPI", "PostgreSQL"],
    "match_score": 0.92
  }
]
```

---

### Applications

#### `POST /api/v1/applications`
Submit a job application.

**Request Body:**
```json
{
  "resume_id": "uuid",
  "job_id": "uuid"
}
```

**Response:**
```json
{
  "id": "uuid",
  "resume_id": "uuid",
  "job_id": "uuid",
  "match_score": 0.85,
  "status": "applied",
  "created_at": "2024-01-30T10:00:00"
}
```

---

#### `GET /api/v1/applications`
List applications with optional filters.

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `resume_id` | UUID | null | Filter by resume |
| `job_id` | UUID | null | Filter by job |
| `status` | string | null | Filter by status |
| `skip` | int | 0 | Number of records to skip |
| `limit` | int | 20 | Maximum records to return |

**Response:**
```json
[
  {
    "id": "uuid",
    "resume_id": "uuid",
    "job_id": "uuid",
    "job_title": "Python Developer",
    "company": "Tech Corp",
    "match_score": 0.85,
    "status": "applied",
    "created_at": "2024-01-30T10:00:00"
  }
]
```

---

#### `GET /api/v1/applications/{application_id}`
Get application details.

**Response:**
```json
{
  "id": "uuid",
  "resume_id": "uuid",
  "job_id": "uuid",
  "job_title": "Python Developer",
  "company": "Tech Corp",
  "match_score": 0.85,
  "status": "screening",
  "created_at": "2024-01-30T10:00:00"
}
```

---

#### `PATCH /api/v1/applications/{application_id}/status`
Update application status.

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `status` | string | New status: `applied`, `screening`, `interview`, `hired`, `rejected` |

**Response:**
```json
{
  "message": "Application status updated to screening"
}
```

---

#### `DELETE /api/v1/applications/{application_id}`
Withdraw/delete an application.

**Response:**
```json
{
  "message": "Application deleted successfully"
}
```

---

## Application Flow

```
1. Job Seeker uploads resume (PDF)
   POST /api/v1/resumes/upload
   ↓
2. System extracts: name, email, skills, education, experience
   ↓
3. System generates AI embedding for matching
   ↓
4. Employer creates job posting
   POST /api/v1/jobs
   ↓
5. Job Seeker views matching jobs
   GET /api/v1/resumes/{id}/matches
   ↓
6. Job Seeker applies to job
   POST /api/v1/applications
   ↓
7. Employer views matching candidates
   GET /api/v1/jobs/{id}/candidates
   ↓
8. Employer updates application status
   PATCH /api/v1/applications/{id}/status
   (applied → screening → interview → hired/rejected)
```

---

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error message here"
}
```

**Common HTTP Status Codes:**
| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request (validation error) |
| 404 | Not Found |
| 500 | Internal Server Error |

---

## Skills Database

The system recognizes 60+ technical skills including:

**Programming Languages:**
Python, Java, JavaScript, TypeScript, C++, C#, Ruby, PHP, Swift, Kotlin, Go, Rust, SQL

**Web Technologies:**
React, Angular, Vue, Node.js, Django, Flask, FastAPI, Laravel, Bootstrap, Tailwind

**Databases:**
MySQL, PostgreSQL, MongoDB, Redis, Firebase, Oracle

**Cloud & DevOps:**
AWS, Azure, GCP, Docker, Kubernetes, Jenkins, Git

**Data Science & AI:**
Machine Learning, Deep Learning, TensorFlow, PyTorch, Pandas, NumPy

**Mobile:**
Android, iOS, React Native, Flutter
