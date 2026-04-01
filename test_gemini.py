import os
import time
from google import genai
from google.api_core import exceptions
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("AIzaSyCdw7cQGuCEItccDMb5FfFOr4NSKZNiB4s"))

def ask_gemini_with_retry(prompt, retries=3, delay=2):
    for i in range(retries):
        try:
            return client.models.generate_content(
                model='gemini-3.1-flash-lite-preview',
                contents=prompt
            )
        except exceptions.ServiceUnavailable:
            print(f"Server busy... retrying in {delay}s (Attempt {i+1}/{retries})")
            time.sleep(delay)
            delay *= 2  # Exponential backoff (wait longer each time)
    return None

response = ask_gemini_with_retry("Explain gravity simply")

if response:
    print(f"AI: {response.text}")
else:
    print("Tutor is currently resting. Please try again in a minute!")