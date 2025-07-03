import requests
import re
from config import Config
from nlp_processor import extract_keywords # Import the spaCy function

# Ensure that the spaCy model is loaded only once when text_processing is imported
# This is handled within text_processing.py to avoid redundant loading.

def get_ollama_response(prompt_text, model=Config.OLLAMA_MODEL):
    messages = [
        {
            "role": "system",
            "content": "You are a highly analytical CV matching assistant. Your goal is to provide a precise match score (0-100%) and a concise explanation. Consider both hard skills, soft skills, experience relevance, and keyword presence. A 100% score means an almost perfect, ideal candidate. A 0% score means absolutely no match. Be critical and provide a realistic assessment. Format EXACTLY like this:\nScore: [NUMBER]%\nExplanation: [TEXT]"
        },
        {
            "role": "user",
            "content": prompt_text
        }
    ]

    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": 0.5, # Good balance between determinism and creativity
            "num_ctx": 2000,    # Increased context window for potentially more text
                                # Ensure your Ollama model (e.g., Llama3) supports this or adjust
            "num_predict": 200  # Allow for more detailed explanations
        }
    }

    try:
        response = requests.post(
            f"{Config.OLLAMA_API_BASE_URL}/api/chat",
            json=payload,
            timeout=120
        )
        response.raise_for_status()
        return response.json().get('message', {}).get('content', '')

    except requests.exceptions.Timeout:
        print("\n Timeout! Try these fixes:")
        print("- Reduce CV/job description length")
        print("- Lower model size or use a smaller one like `gemma:2b-instruct`")
        print("- Check CPU usage in Task Manager")
        return None
    except requests.exceptions.ConnectionError:
        print(f"Error: Could not connect to Ollama at {Config.OLLAMA_API_BASE_URL}")
        print("1. Ensure Ollama is running: `ollama serve`")
        print("2. Verify port matches config.py")
        return None
    except Exception as e:
        print(f"Ollama API Error: {str(e)}")
        return None

def evaluate_cv_with_ai(job_description, cv_text):
    # Use MAX_PROMPT_TEXT_LENGTH from Config for consistency
    max_text_for_llm = getattr(Config, 'MAX_PROMPT_TEXT_LENGTH', 2500)
    max_keywords_display = getattr(Config, 'MAX_KEYWORDS_IN_PROMPT', 30)

    # 1. Extract Keywords from Job Description and CV using spaCy
    jd_keywords = extract_keywords(job_description)
    cv_keywords = extract_keywords(cv_text)

    # Convert lists of keywords to strings for inclusion in the prompt
    # Limit the number of keywords to avoid prompt overflow, especially for very long texts
    jd_keywords_str = ", ".join(jd_keywords[:max_keywords_display])
    cv_keywords_str = ", ".join(cv_keywords[:max_keywords_display])

    # 2. Construct the enhanced prompt with extracted keywords
    prompt = f"""
    Analyze this job application and candidate CV for a precise match score. Focus on the following aspects:
    - **Required Skills:** Are all key technical and soft skills present? (e.g., Python, SQL, communication, teamwork)
    - **Experience Relevance:** How closely does the candidate's past work experience align with the job's duties and responsibilities?
    - **Keywords:** Are important keywords from the job description found in the CV?
    - **Years of Experience:** Does the candidate meet the stated years of experience requirements?
    - **Education:** Is the educational background relevant?

    Here's a breakdown of extracted keywords for closer evaluation:

    [JOB DESCRIPTION DETAILS]
    Extracted Keywords: {jd_keywords_str}
    Full Job Description (Excerpt): {job_description[:max_text_for_llm]}

    [CANDIDATE CV DETAILS]
    Extracted Keywords: {cv_keywords_str}
    Full Candidate CV (Excerpt): {cv_text[:max_text_for_llm]}

    Provide:
    1. Match score (0-100%)
    2. Brief explanation highlighting key strengths and weaknesses based on the criteria above and the provided keywords.

    Format EXACTLY like this:
    Score: [NUMBER]%
    Explanation: [TEXT]
    """

    response_text = get_ollama_response(prompt)

    if not response_text:
        return 0, "AI service unavailable"

    print("Raw AI response:\n", response_text)  # Optional debug log

    # Parse score and explanation using regex
    score = 0
    explanation = "No explanation provided"

    score_match = re.search(r"Score:\s*(\d+)%", response_text, re.IGNORECASE)
    if score_match:
        score = int(score_match.group(1))
        score = max(0, min(score, 100))

    explanation_match = re.search(r"Explanation:\s*([\s\S]+)", response_text, re.IGNORECASE)
    if explanation_match:
        explanation = explanation_match.group(1).strip()

    return score, explanation