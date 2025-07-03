from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
import shutil
from dotenv import load_dotenv
from typing import List, Dict, Optional, Tuple

from config import Config
from cv_parser import parse_cv
from ai_matcher import evaluate_cv_with_ai
# IMPORTANT: Import semantic_match_score and extract_keywords from nlp_processor
from nlp_processor import extract_keywords, semantic_match_score # <--- ADD THIS LINE
from models import init_db, add_cv_to_db, get_all_cvs

# Constants
ALLOWED_EXTENSIONS = {'pdf', 'docx'}
MAX_FILE_SIZE_MB = 5
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Setup folders and DB
def setup_application():
    """Initialize application resources."""
    # Load environment variables
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

    # Create required directories
    app.config['UPLOAD_FOLDER_PATH'] = os.path.join(os.path.dirname(__file__), app.config['UPLOAD_FOLDER'])
    app.config['MATCHED_CVS_FOLDER_PATH'] = os.path.join(os.path.dirname(__file__), app.config['MATCHED_CVS_FOLDER'])

    os.makedirs(app.config['UPLOAD_FOLDER_PATH'], exist_ok=True)
    os.makedirs(app.config['MATCHED_CVS_FOLDER_PATH'], exist_ok=True)

    # Initialize database
    with app.app_context():
        init_db()

setup_application()

def allowed_file(filename: str) -> bool:
    """Check if file has allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_cv_file(cv_file, job_description: str, upload_folder: str, matched_folder: str) -> Optional[Dict]:
    """Process a single CV file and return match results."""
    try:
        if cv_file.filename == '' or not allowed_file(cv_file.filename):
            return None

        filename = secure_filename(cv_file.filename)
        file_path = os.path.join(upload_folder, filename)

        # Save file temporarily
        cv_file.save(file_path)

        # Check file size
        if os.path.getsize(file_path) > MAX_FILE_SIZE_BYTES:
            os.remove(file_path)
            return {
                "name": filename,
                "score": 0,
                "explanation": "File size exceeds maximum allowed (5MB)",
                "pdf_link": ""
            }

        # Extract text from CV
        cv_text = parse_cv(file_path)

        if not cv_text:
            os.remove(file_path)
            return {
                "name": filename,
                "score": 0,
                "explanation": "Could not parse CV content",
                "pdf_link": ""
            }

        # Save to DB (Consider moving this AFTER semantic check if you only want to store "matched" CVs)
        # For now, keeping it here as per your original code.
        add_cv_to_db(filename, file_path, cv_text)

        # --- NEW SEMANTIC SIMILARITY PRE-FILTERING ---
        jd_keywords = extract_keywords(job_description)
        cv_keywords = extract_keywords(cv_text)

        # Join keywords for semantic comparison
        jd_keywords_str = " ".join(jd_keywords)
        cv_keywords_str = " ".join(cv_keywords)

        # You might want to get this threshold from Config
        SEMANTIC_SIMILARITY_THRESHOLD = getattr(Config, 'SEMANTIC_SIMILARITY_THRESHOLD', 0.4) # <--- ADD TO config.py

        sim_score = semantic_match_score(cv_keywords_str, jd_keywords_str)

        # Optionally set a threshold to skip low matches
        if sim_score < SEMANTIC_SIMILARITY_THRESHOLD:
            # Clean up the temporarily saved file if it's skipped
            os.remove(file_path)
            return {
                "name": filename,
                "score": 0, # Or some other specific value like -1 to indicate skipped
                "explanation": f"Low semantic similarity ({sim_score:.2f}), skipped detailed AI evaluation.",
                "pdf_link": "" # No PDF link if not stored in matched_cvs
            }
        # --- END NEW SEMANTIC SIMILARITY PRE-FILTERING ---


        # Otherwise, proceed with AI evaluation
        score, explanation = evaluate_cv_with_ai(job_description, cv_text)

        # Copy to matched folder
        matched_cv_path = os.path.join(matched_folder, filename)
        shutil.copy(file_path, matched_cv_path)

        # Clean up original upload
        os.remove(file_path)

        return {
            "name": filename,
            "score": score,
            "explanation": explanation,
            "pdf_link": f"/matched_cvs/{filename}"
        }

    except Exception as e:
        app.logger.error(f"Error processing file {cv_file.filename}: {str(e)}")
        # Ensure the file is removed even on unexpected errors during processing
        if os.path.exists(file_path):
            os.remove(file_path)
        return None

@app.route('/api/match', methods=['POST'])
def match_cvs():
    """Endpoint for matching CVs against a job description."""
    # Validate request
    if 'job_description' not in request.form:
        return jsonify({"error": "Job description is required"}), 400

    if 'cvs' not in request.files:
        return jsonify({"error": "No CV files provided"}), 400

    job_description = request.form['job_description']
    cv_files = request.files.getlist('cvs')

    if not job_description.strip():
        return jsonify({"error": "Job description cannot be empty"}), 400

    if not cv_files or all(file.filename == '' for file in cv_files):
        return jsonify({"error": "No valid CV files provided"}), 400

    # Process each CV
    results = []
    for cv_file in cv_files:
        result = process_cv_file(
            cv_file,
            job_description,
            app.config['UPLOAD_FOLDER_PATH'],
            app.config['MATCHED_CVS_FOLDER_PATH']
        )
        if result:
            results.append(result)

    # Sort by score (descending)
    results.sort(key=lambda x: x['score'], reverse=True)

    return jsonify({
        "count": len(results),
        "matches": results
    })

@app.route('/matched_cvs/<filename>')
def download_matched_cv(filename: str):
    """Endpoint for downloading matched CVs."""
    try:
        return send_from_directory(
            app.config['MATCHED_CVS_FOLDER_PATH'],
            filename,
            as_attachment=True
        )
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404

@app.route('/')
def serve_index():
    """Serve the frontend application."""
    # Assuming ab.html is in the parent directory of your Flask app
    return send_from_directory('../', 'ab.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)