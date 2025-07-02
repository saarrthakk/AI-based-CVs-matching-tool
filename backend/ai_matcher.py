import requests
import re
from config import Config

def get_ollama_response(prompt_text, model=Config.OLLAMA_MODEL):
    messages = [
        {
            "role": "system", 
            "content": "You are a CV matching assistant. Provide:\n1. Score (0-100%)\n2. Concise explanation\n\nFormat EXACTLY like this:\nScore: [NUMBER]%\nExplanation: [TEXT]"
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
            "temperature": 0.3,
            "num_ctx": 1024,
            "num_predict": 100
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
    MAX_LENGTH = 750
    
    prompt = f"""
    Analyze this job application:

    [JOB DESCRIPTION]
    {job_description[:MAX_LENGTH]}

    [CANDIDATE CV]
    {cv_text[:MAX_LENGTH]}

    Provide:
    1. Match score (0-100%)
    2. Brief explanation

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

    explanation_match = re.search(r"Explanation:\s*(.+)", response_text, re.IGNORECASE)
    if explanation_match:
        explanation = explanation_match.group(1).strip()

    return score, explanation
