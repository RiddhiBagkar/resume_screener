import sys
import json
import os
import pdfplumber

from score import evaluate_resume_fixed


def extract_text(pdf_path):
    """Extract text from a PDF."""
    with pdfplumber.open(pdf_path) as pdf:
        text = "\n".join(page.extract_text() or "" for page in pdf.pages)

    if not text.strip():
        raise ValueError("PDF contains no extractable text")

    return text


def error_response(message):
    """Return a standard JSON error response."""
    return {
        "success": False,
        "error": message
    }


def validate_result(result):
    """Validate Gemini's structured screening result."""

    required_fields = [
        "candidate_name",
        "match_score",
        "key_strengths",
        "missing_skills",
        "final_verdict",
        "explanation"
    ]

    # Check required fields
    for field in required_fields:
        if field not in result:
            raise ValueError(f"Missing field: {field}")

    # Validate match_score
    score = result["match_score"]

    if not isinstance(score, (int, float)) or isinstance(score, bool):
        raise ValueError("match_score must be a number")

    if not 0 <= score <= 100:
        raise ValueError("match_score must be between 0 and 100")

    # Validate lists
    if not isinstance(result["key_strengths"], list):
        raise ValueError("key_strengths must be a list")

    if not isinstance(result["missing_skills"], list):
        raise ValueError("missing_skills must be a list")

    # Validate strings
    if not isinstance(result["candidate_name"], str):
        raise ValueError("candidate_name must be a string")

    if not isinstance(result["final_verdict"], str):
        raise ValueError("final_verdict must be a string")

    if not isinstance(result["explanation"], str):
        raise ValueError("explanation must be a string")

    return result


def main():
    try:
        # -------------------------------------------------
        # 1. Read JSON input
        # -------------------------------------------------

        if len(sys.argv) < 2:
            print(json.dumps(error_response("No JSON input provided")))
            sys.exit(1)

        raw_input = sys.argv[1]

        try:
            data = json.loads(raw_input)
        except json.JSONDecodeError:
            print(json.dumps(error_response("Invalid JSON input")))
            sys.exit(1)

        # -------------------------------------------------
        # 2. Validate input
        # -------------------------------------------------

        resume_path = data.get("resume_path")
        job_description = data.get("job_description")

        if not resume_path:
            print(json.dumps(error_response("resume_path is required")))
            sys.exit(1)

        if not job_description:
            print(json.dumps(error_response("job_description is required")))
            sys.exit(1)

        # -------------------------------------------------
        # 3. Check resume
        # -------------------------------------------------

        if not os.path.isfile(resume_path):
            print(json.dumps(error_response("Resume PDF not found")))
            sys.exit(1)

        # -------------------------------------------------
        # 4. Extract resume text
        # -------------------------------------------------

        try:
            resume_text = extract_text(resume_path)

        except Exception as e:
            print(
                json.dumps(
                    error_response(
                        f"Unable to read or extract text from PDF: {str(e)}"
                    )
                )
            )
            sys.exit(1)

        # -------------------------------------------------
        # 5. Gemini screening
        # -------------------------------------------------

        try:
            gemini_result = evaluate_resume_fixed(
                resume_text,
                job_description
            )

        except Exception as e:
            print(
                json.dumps(
                    error_response(
                        f"Gemini API error: {str(e)}"
                    )
                )
            )
            sys.exit(1)

        # -------------------------------------------------
        # 6. Parse Gemini JSON
        # -------------------------------------------------

        try:
            result = json.loads(gemini_result)

        except json.JSONDecodeError:
            print(
                json.dumps(
                    error_response(
                        "Invalid JSON response received from Gemini"
                    )
                )
            )
            sys.exit(1)

        # -------------------------------------------------
        # 7. Validate Gemini result
        # -------------------------------------------------

        try:
            result = validate_result(result)

        except ValueError as e:
            print(
                json.dumps(
                    error_response(
                        f"Invalid Gemini result: {str(e)}"
                    )
                )
            )
            sys.exit(1)

        # -------------------------------------------------
        # 8. Add success flag
        # -------------------------------------------------

        final_result = {
            "success": True,
            **result
        }

        # -------------------------------------------------
        # 9. Output ONLY JSON
        # -------------------------------------------------

        print(
            json.dumps(
                final_result,
                ensure_ascii=False
            )
        )

        sys.exit(0)

    except Exception as e:
        print(
            json.dumps(
                error_response(
                    f"Unexpected error: {str(e)}"
                )
            )
        )
        sys.exit(1)


if __name__ == "__main__":
    main()