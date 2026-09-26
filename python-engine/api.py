from flask import Flask, request, jsonify
import subprocess
import json
import tempfile
import os
from pathlib import Path

app = Flask(__name__)

DATA_FILE = Path(__file__).parent / "data" / "candidates.json"


@app.route("/screen", methods=["POST"])
def screen_resume():

    # Get job description
    job_description = request.form.get("job_description", "")

    # Get uploaded resume
    resume = request.files.get("resume")

    if not resume:
        return jsonify({
            "success": False,
            "error": "No resume file received"
        }), 400

    # Save resume temporarily
    temp_dir = tempfile.gettempdir()
    resume_path = os.path.join(temp_dir, resume.filename)

    resume.save(resume_path)

    # Prepare data for existing Python screening engine
    data = {
        "resume_path": resume_path,
        "job_description": job_description
    }

    try:
        result = subprocess.run(
            ["python3", "n8n_runner.py", json.dumps(data)],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            return jsonify({
                "success": False,
                "error": result.stderr
            }), 500

        output = json.loads(result.stdout)

        return jsonify(output)

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

    finally:
        # Delete temporary resume after processing
        if os.path.exists(resume_path):
            os.remove(resume_path)


@app.route("/result", methods=["POST"])
def receive_result():

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "No data received"
        }), 400

    DATA_FILE.parent.mkdir(exist_ok=True)

    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                candidates = json.load(f)
        except:
            candidates = []
    else:
        candidates = []

    candidates.append(data)

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(candidates, f, indent=4)

    return jsonify({
        "success": True,
        "message": "Result received successfully"
    })


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok"
    })


app.run(host="0.0.0.0", port=5000)