from ai_tutor.gemini_client import generate_ai_response
from ai_tutor.prompts import build_topic_extraction_prompt

def identify_current_topic(chat_messages):
    """
    Analyzes the last few chat messages to extract the specific 
    academic sub-topic being discussed.
    """
    if not chat_messages:
        return "General Overview"

    # Format history for Gemini
    history_text = "\n".join([f"{m.sender}: {m.message}" for m in chat_messages[-8:]])

    prompt=build_topic_extraction_prompt(history_text)
     
    topic = generate_ai_response(prompt)
    return topic.strip()