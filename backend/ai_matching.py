import os
import json
import requests
from config import GEMINI_API_KEY

# API URL for the Gemini model
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={GEMINI_API_KEY}"

# this function uses the Gemini model to get a match score and explanation for the CV against job description
def get_ai_match(cv_text, job_description):
    
    # this will give a mock response if the API key is not set
    if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_GEMINI_API_KEY":
        
        print("Warning: GEMINI_API_KEY not found or not set. Returning mock data.")
        mock_response = {
            "match_score": 8,
            "explanation": "This is a mock response because the API key is not configured."
        }
        return json.dumps(mock_response)

    # constructing a prompt for the gemini model
    prompt = f"""
    You are an advanced AI recruitment analyst. Your task is to perform a strict, detailed analysis of a candidate's CV against a job description. Follow these steps precisely:

    1.  **Identify Core Requirements:** First, from the **Job Description** below, identify the 5-7 most critical skills, technologies, and years of experience required. These are the core requirements.
    2.  **Scan for Evidence:** Second, meticulously scan the **Candidate's CV** to find direct evidence for each of the core requirements you identified.
    3.  **Calculate Score:** Third, calculate a `match_score` from 1 (no match) to 10 (perfect match). The score must be based *only* on the presence of the core requirements in the CV. A candidate missing several core requirements cannot receive a high score, even if they have other skills. A perfect 10 requires strong evidence for all core requirements.
    4.  **Write Explanation:** Fourth, write a concise `explanation` that justifies your score. Specifically mention 2-3 key requirements from the job description that the candidate demonstrably meets and, if applicable, any critical requirements that appear to be missing.

    **Output Format:** Your final output must be a single, clean JSON object and nothing else. Do not include any text, conversational phrases, or markdown formatting like ```json before or after the JSON object.

    **Job Description:**
    ---
    {job_description}
    ---

    **Candidate's CV:**
    ---
    {cv_text}
    ---

    **Your JSON analysis:**
    """

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }

    headers = {
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(API_URL, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        
        result = response.json()
        
        if 'candidates' in result and len(result['candidates']) > 0:
            content = result['candidates'][0]['content']['parts'][0]['text']
            cleaned_content = content.strip().lstrip('```json').rstrip('```').strip()
            return cleaned_content
        else:
            raise ValueError("Invalid response format from AI API. No candidates found.")

    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        error_response = {
            "match_score": 0,
            "explanation": f"Failed to communicate with the AI service: {e}"
        }
        return json.dumps(error_response)
    except (ValueError, KeyError) as e:
        print(f"Error processing AI response: {e}")
        error_response = {
            "match_score": 0,
            "explanation": f"Could not parse the response from the AI service: {e}"
        }
        return json.dumps(error_response)