import time
from django.conf import settings
from google import genai
from google.api_core import exceptions

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