import os
import sys
import warnings
from dotenv import load_dotenv
from google import genai
import pdfplumber
import time 
# Silence general internal tracking telemetry warnings
warnings.filterwarnings("ignore", category=UserWarning, module="google.genai")

# Force pull local variables securely
load_dotenv(override=True)

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ Error: GEMINI_API_KEY not found in your .env file.")
    sys.exit(1)

# PERMANENT PYTHON 3.14 COMPATIBILITY FIX:
# Pass custom HTTP options via a standard dictionary configuration.
# This prevents Pydantic validation errors while establishing direct routing paths.
client = genai.Client(
    api_key=api_key
)

def extract_text(pdf_path):
    """Safely extracts text strings from the target PDF file."""
    with pdfplumber.open(pdf_path) as pdf:
        return "\n".join(page.extract_text() or "" for page in pdf.pages)

def evaluate_resume_fixed(resume_text, job_desc):

    prompt = f"""

You are an expert technical recruiter.

Analyze the candidate's resume against the provided job description.

JOB DESCRIPTION:
{job_desc}

RESUME:
{resume_text}

Return ONLY a valid JSON object.

Do not use Markdown.
Do not use ```json fences.
Do not include explanations outside the JSON.

Use exactly this structure:

{{
  "candidate_name": "Candidate name from the resume",
  "match_score": 0,
  "key_strengths": [
    "strength 1",
    "strength 2"
  ],
  "missing_skills": [
    "missing skill 1",
    "missing skill 2"
  ],
  "final_verdict": "Strong Fit",
  "explanation": "Brief explanation of the candidate's match with the job description."
}}

Rules:
- match_score must be a number between 0 and 100.
- key_strengths must always be a JSON array of strings.
- missing_skills must always be a JSON array of strings.
- final_verdict must be one of: "Strong Fit", "Potential Fit", "Not a Fit".
- explanation must be a string.
- candidate_name should be taken from the resume. If the name cannot be determined, use "Unknown".
- Return valid JSON only.
"""

    for attempt in range(3):
        try:
            response = client.interactions.create(
                model="gemini-3.6-flash",
                input=prompt
            )

            return response.output_text

        except Exception as e:
            if "503" in str(e) and attempt < 2:
                print(f"⚠️ Gemini temporarily unavailable. Retrying...")
                time.sleep(3 * (attempt + 1))
            else:
                raise

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 score.py <path_to_pdf>")
        sys.exit(1)
        
    pdf_path = sys.argv[1]
    
    sample_job_description = """
    We are looking for a Python Developer with experience in data extraction, 
    working with APIs, git version control, and setting up isolated virtual environments.
    """
    
    print("Reading resume...")
    text = extract_text(pdf_path)
    
    print("Analyzing with Gemini AI (Stable Route)...")
    try:
        analysis = evaluate_resume_fixed(text, sample_job_description)
        print("\n--- SCREENING REPORT ---")
        print(analysis)
    except Exception as e:
        print(f"\n❌ Network Request Failed!") 
        print(f"Error Details: {e}")
