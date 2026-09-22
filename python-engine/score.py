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
You are an expert technical recruiter. Analyze this resume against the job description.

Job Description:
{job_desc}

Resume Text:
{resume_text}

Provide your response in the following exact format:

---
### 📊 MATCH SCORE: [0-100]%

### ✅ KEY STRENGTHS:
- [Strength 1]
- [Strength 2]

### ❌ MISSING SKILLS & GAPS:
- [Gap 1]
- [Gap 2]

### 📝 FINAL VERDICT:
[Strong Fit / Potential Fit / Not a Fit] - [1-2 sentences explaining why]
---
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
