from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
import shutil
from dotenv import load_dotenv

from config import Config
from cv_parser import parse_cv
from ai_matcher import evaluate_cv_with_ai
from models import init_db, add_cv_to_db, get_all_cvs

# Load environment variables from .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

# Initialize Flask app and config
app = Flask(__name__)
app.config.from_object(Config)

# Folder setup
UPLOAD_FOLDER_PATH = os.path.join(os.path.dirname(__file__), app.config['UPLOAD_FOLDER'])
MATCHED_CVS_FOLDER_PATH = os.path.join(os.path.dirname(__file__), app.config['MATCHED_CVS_FOLDER'])

os.makedirs(UPLOAD_FOLDER_PATH, exist_ok=True)
os.makedirs(MATCHED_CVS_FOLDER_PATH, exist_ok=True)

# Initialize DB
with app.app_context():
    init_db()

# API endpoint to match CVs
@app.route('/api/match', methods=['POST'])
def match_cvs():
    if 'job_description' not in request.form:
        return jsonify({"error": "Job description is missing"}), 400
    if 'cvs' not in request.files:
        return jsonify({"error": "No CV files provided"}), 400

    job_description = request.form['job_description']
    cv_files = request.files.getlist('cvs')

    results = []

    for cv_file in cv_files:
        if cv_file.filename == '':
            continue

        filename = secure_filename(cv_file.filename)
        file_path = os.path.join(UPLOAD_FOLDER_PATH, filename)
        cv_file.save(file_path)

        # Extract text from CV
        cv_text = parse_cv(file_path)

        if cv_text:
            # Save to DB
            add_cv_to_db(filename, file_path, cv_text)

            # Get AI match score
            score, explanation = evaluate_cv_with_ai(job_description, cv_text)

            # Copy to matched folder
            matched_cv_path = os.path.join(MATCHED_CVS_FOLDER_PATH, filename)
            shutil.copy(file_path, matched_cv_path)

            results.append({
                "name": filename,
                "score": score,
                "explanation": explanation,
                "pdf_link": f"/matched_cvs/{filename}"
            })
        else:
            results.append({
                "name": filename,
                "score": 0,
                "explanation": "Could not parse CV content.",
                "pdf_link": ""
            })

    # Sort by score
    results.sort(key=lambda x: x['score'], reverse=True)

    return jsonify({"matches": results})

# Serve matched CVs for download
@app.route('/matched_cvs/<filename>')
def download_matched_cv(filename):
    return send_from_directory(MATCHED_CVS_FOLDER_PATH, filename)

# Serve index page
@app.route('/')
def serve_index():
    return send_from_directory('../', 'ab.html')

# Run server
if __name__ == '__main__':
    app.run(debug=True, port=5000)
