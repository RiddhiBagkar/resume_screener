# AI Resume Screening System

An automated resume screening prototype that uses **n8n**, **Python** and **Google Gemini AI** to compare a candidate's resume with a job description and present the results to HR on a dashboard.

> **Project status:** working prototype developed as a college group project. It runs on a development machine and has considerable scope for future improvement (see [Future Scope](#future-scope)).

---

## Table of Contents

- [Purpose of the Project](#purpose-of-the-project)
- [Why We Chose This Project](#why-we-chose-this-project)
- [How It Works (Our Workflow)](#how-it-works-our-workflow)
- [Traditional ATS vs Our System](#traditional-ats-vs-our-system)
- [Technologies Used](#technologies-used)
- [Project Structure](#project-structure)
- [Running the Project](#running-the-project)
- [Current Limitations](#current-limitations)
- [Future Scope](#future-scope)
- [Documentation](#documentation)

---

## Purpose of the Project

Screening resumes manually is slow and repetitive. A recruiter has to read every resume, compare it with the job requirements, and note down who looks suitable.

The purpose of this project is to **automate the first stage of resume screening**. For each resume, the system:

- reads the resume PDF and the job description,
- uses AI to judge how well the candidate matches the job,
- produces a structured result: match score, key strengths, missing skills, final verdict and a short explanation,
- stores the result and shows it to HR on a dashboard.

The system is meant to **support** HR by shortlisting quickly. The final hiring decision stays with a human.

## Why We Chose This Project

- Resume screening is a real, common problem that combines **AI, automation, document processing and backend development** in one project.
- It let us work with several technologies together: Python, an AI API, workflow automation (n8n), Docker, Linux (Ubuntu/WSL) and a web dashboard.
- The output is easy to understand and evaluate: a score, strengths, gaps and an explanation for each candidate.
- It has clear room to grow into a larger system, which made it a good base for a learning project.

---

## How It Works (Our Workflow)

```text
Resume + Job Description
        ↓
n8n (running in Docker)
        ↓  HTTP POST (resume PDF + job_description)
Python Flask API  (/screen)
        ↓
Save resume temporarily → Extract text from PDF
        ↓
Google Gemini AI compares resume with job description
        ↓
Validated structured JSON result
        ↓
n8n extracts the result fields
        ↓
Result stored in data/candidates.json
        ↓
Streamlit HR Dashboard
```

*In our original design, resumes entered through a Google Form and Google Drive, and results were planned for Google Sheets. In the current version, results are stored in a JSON file and displayed in a Streamlit dashboard.*

**Result returned for each candidate:**

```json
{
  "candidate_name": "Candidate Name",
  "match_score": 82,
  "key_strengths": ["Python", "SQL"],
  "missing_skills": ["Advanced Power BI"],
  "final_verdict": "Potential Fit",
  "explanation": "Short explanation of the score"
}
```

---

## Traditional ATS vs Our System

### How a traditional ATS typically works

An Applicant Tracking System (ATS) collects applications and helps recruiters manage them. For screening, most traditional systems work like this:

```text
Resume uploaded
        ↓
Resume parsed into fields (name, skills, education, experience)
        ↓
Keywords from the job posting matched against the resume
        ↓
Candidates ranked / filtered by keyword match
        ↓
Recruiter reviews the shortlist
```

Matching is mainly **keyword-based**, so a resume may be ranked low if it describes the same skill in different words. A typical ATS also gives a rank or score, but not always a readable reason for it.

### How our system works

```text
Resume PDF + Job Description
        ↓
AI reads and understands both
        ↓
Match score + strengths + missing skills + verdict + explanation
        ↓
HR reviews results on a dashboard
```

### Comparison

| Aspect | Traditional ATS | Our System |
|---|---|---|
| Matching method | Mostly keyword matching | AI (Gemini) compares the resume with the job description as a whole |
| Output | Rank, score or filter result | Score, key strengths, missing skills, final verdict and written explanation |
| Explainability | Often limited | Every result comes with an explanation |
| Flexibility | Depends on the vendor's rules | Prompt and output format can be changed in our own code |
| Workflow | Usually a fixed product workflow | Built with n8n, so steps can be changed or extended |
| Scope | Full recruitment management (job posting, candidate tracking, etc.) | **Screening only**, at prototype level |

**Note:** our system is not a replacement for a full ATS. It focuses on one part of the process, screening, and explores a different way of doing it. AI results can be wrong or vary between runs, so they should be reviewed by a person.

---

## Technologies Used

| Technology | Use |
|---|---|
| Python | Backend processing |
| pdfplumber | Extracting text from PDF resumes |
| Google Gemini API | Analysing the resume against the job description |
| Flask | HTTP API used by n8n |
| n8n | Workflow automation |
| Docker | Running n8n |
| Streamlit | HR dashboard |
| JSON | Data exchange and result storage |
| Ubuntu (WSL) | Development and execution environment |
| Git / GitHub | Version control |

---

## Project Structure

```text
python-engine/
├── api.py               Flask API (/screen, /result, /health)
├── app.py               Streamlit HR dashboard
├── extract.py           PDF text extraction
├── score.py             Gemini-based resume evaluation
├── n8n_runner.py        n8n interface with input/output validation
├── requirements.txt     Python dependencies
└── data/
    └── candidates.json  Stored screening results
```

---

## Running the Project

The Python backend runs on Ubuntu (WSL) and n8n runs in Docker.

```bash
cd resume_screener/python-engine
source venv/bin/activate
pip install -r requirements.txt

# Add your Gemini API key to a local .env file (not committed to Git)

# Start the Flask backend (port 5000)
python3 api.py

# In another terminal, start the dashboard
streamlit run app.py     # opens at http://localhost:8501
```

n8n (in Docker) sends requests to the Flask server using the WSL IP address, for example `http://<WSL-IP>:5000/screen`, because `localhost` inside Docker does not point to the WSL server.

---

## Current Limitations

- Only text-based PDFs are supported; scanned resumes need OCR.
- Results are stored in a JSON file, which is not suitable for large amounts of data.
- The servers are started manually and run on a personal computer.
- The n8n connection uses a fixed WSL IP address.
- The API has no authentication.
- AI scoring can vary and depends on Gemini API availability and usage limits.

---

## Future Scope

- **Database integration:** replace `candidates.json` with a proper database such as MySQL or PostgreSQL.
- **OCR support** for scanned resumes.
- **Advanced resume parsing:** structured extraction of skills, education, experience, certifications and projects.
- **Semantic matching** using embeddings or vector databases.
- **Better scoring:** multi-factor scoring and machine-learning-based candidate classification.
- **Batch processing** of multiple resumes at once.
- **Stronger API:** authentication, input validation and logging.
- **Cloud / server deployment:** run Flask and n8n continuously on a Linux server using Docker, with HTTPS, backups and monitoring.
- **Richer dashboard:** filtering, sorting and candidate comparison for HR.

---

## Documentation

Detailed documentation for each part of the project:

- [Python Implementation](docs/Python_Implementation.pdf)
- [Ubuntu / WSL Environment](docs/Ubuntu_WSL_Environment.pdf)
- [Python–n8n Integration and Workflow](docs/Python_n8n_Integration_and_Workflow.pdf)
- [n8n_in_ai_resume_screening_system](docs/n8n_in_AI_Resume_Screening_System.pdf)
