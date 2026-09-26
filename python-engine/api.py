from flask import Flask, request, jsonify
import subprocess
import json

app = Flask(__name__)

@app.route("/screen", methods=["POST"])
def screen_resume():
    data = request.get_json()

    result = subprocess.run(
        ["python", "n8n_runner.py", json.dumps(data)],
        capture_output=True,
        text=True
    )

    return jsonify(json.loads(result.stdout))


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


app.run(host="0.0.0.0", port=5000)
