from openai import OpenAI
import os

# Ensure OPENAI_API_KEY is loaded from .env
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

loaded_key = os.getenv('OPENAI_API_KEY')
print(f"DEBUG: Value of OPENAI_API_KEY from .env: '{loaded_key}'")
if loaded_key:
    print(f"DEBUG: First 5 characters: {loaded_key[:5]}")
else:
    print("DEBUG: OPENAI_API_KEY is None or empty!")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_gpt_response(prompt_text, model="gpt-3.5-turbo"):
    """Sends a prompt to the OpenAI GPT model and returns the response."""
    try:
        chat_completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant for CV matching. Provide a score out of 100 and a concise explanation."},
                {"role": "user", "content": prompt_text}
            ],
            temperature=0.7, # Controls randomness: lower for more focused, higher for more creative
            max_tokens=300 # Limit response length
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return None

def evaluate_cv_with_ai(job_description, cv_text):
    """
    Evaluates a CV against a job description using GPT-3.5.
    Returns a score and an explanation.
    """
    prompt = f"""
    Job Description:
    ---
    {job_description}
    ---

    Candidate CV:
    ---
    {cv_text}
    ---

    Based on the Job Description and the Candidate CV, evaluate the fit.
    Provide a match score (0-100) and a concise explanation (2-3 sentences)
    highlighting key strengths and weaknesses relative to the job description.

    Format your response strictly as:
    Score: [SCORE]%
    Explanation: [EXPLANATION TEXT]
    """
    response_text = get_gpt_response(prompt)

    if response_text:
        score = 0
        explanation = "N/A"
        lines = response_text.split('\n')
        for line in lines:
            if line.startswith("Score:"):
                try:
                    score_str = line.split("Score:")[1].strip().replace('%', '')
                    score = int(float(score_str)) # Use float for robustness, then int
                except ValueError:
                    pass
            elif line.startswith("Explanation:"):
                explanation = line.split("Explanation:")[1].strip()
        return score, explanation
    return 0, "Failed to get AI response."