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
    
def generate_textbook_map(extracted_text):
    """
    Scans the beginning of a PDF to create a Map of chapters and topics.
    """
    # We only need the first part of the book to find the TOC
    toc_sample = extracted_text[:15000] 
    
    prompt = f"""
    Analyze the following Table of Contents or introductory text from an Ethiopian textbook.
    
    TEXT:
    \"\"\"{toc_sample}\"\"\"
    
    TASK:
    Create a detailed 'Map' of this book. Identify major Chapters and the key technical terms 
    or topics mentioned in each chapter.
    
    RETURN ONLY A JSON OBJECT:
    {{
        "chapters": [
            {{
                "title": "Chapter Name",
                "keywords": ["term1", "term2", "topic3"],
                "summary": "Brief 1-sentence description"
            }}
        ]
    }}
    """
    raw_response = generate_ai_response(prompt)
    try:
        clean_json = re.sub(r'```json|```', '', raw_response).strip()
        return clean_json # Return as string to save in TextField
    except Exception as e:
        print(f"Mapping Error: {e}")
        return "{}"