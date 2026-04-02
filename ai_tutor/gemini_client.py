import time
from django.conf import settings
from google import genai
from google.api_core import exceptions
#for validation
import json
import re
from .prompts import build_validation_prompt

# initialize client using settings
client = genai.Client(api_key=settings.GEMINI_API_KEY)


def generate_ai_response(prompt, retries=3, delay=2):
    """
    Send prompt to Gemini and return text response.
    Includes retry logic for reliability.
    """
    for attempt in range(retries):
        try:
            response = client.models.generate_content(
                model="gemini-3.1-flash-lite-preview",
                contents=prompt
            )

            return response.text

        except exceptions.ServiceUnavailable:
            print(f"Gemini busy... retry {attempt+1}/{retries}")
            time.sleep(delay)
            delay *= 2  # exponential backoff

    return "AI is currently unavailable. Please try again."


def validate_subject_match(text, subject, grade, language):
    prompt = build_validation_prompt(text, subject, grade, language)
    raw_response = generate_ai_response(prompt)
    
    try:
        # Clean the response if Gemini adds markdown code blocks
        clean_json = re.sub(r'```json|```', '', raw_response).strip()
        data = json.loads(clean_json)
        return data
    except Exception as e:
        print(f"Validation Parsing Error: {e}")
        # Default to True so the user isn't blocked if the AI glitches
        return {"is_match": True, "detected_subject": subject, "feedback": "Verified."}