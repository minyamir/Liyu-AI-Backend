def build_tutor_prompt(user_name, subject, grade, field, language, user_message, context_from_books, chat_history, is_first_message=False):
    """
    Build a structured, context-aware prompt for Liyu Learn AI.
    """
    system_identity = (
        f"You are 'Liyu AI', a supportive and brilliant tutor for {user_name} in Ethiopia. "
        f"You are currently helping with {subject} for Grade {grade}."
        "Your goal is to help the student understand the 'why' behind concepts."
    )
    
    book_instruction = ""
    if context_from_books:
        book_instruction = (
            "\n--- ACTIVE STUDY MATERIAL ---\n"
            "You are currently looking at the student's ACTIVE tab. "
            "Use the 'SOURCE' label below to identify if this is the textbook or the student's own notes.\n"
            f"{context_from_books}\n"
            "INSTRUCTION: Prioritize this text. If the student says 'the book', refer to the OFFICIAL TEXTBOOK. "
            "If they say 'my notes', refer to the USER NOTES.\n"
        )
    memory_instruction = ""
    if chat_history:
        memory_instruction = f"\n--- RECENT CONVERSATION HISTORY ---\n{chat_history}\n"

    greeting_instruction = f"Greet {user_name} in Amharic warmly." if is_first_message else "Do not repeat greetings; continue the helpful tutoring."

    language_logic = ( 
        f"{greeting_instruction} "
        "Explain technical terms in English but use Amharic for encouragement (e.g., 'Gobez!', 'Berta!'). "
        "If the user asks in Amharic, respond primarily in Amharic with English terms in brackets."
    )

    return f"""
            {system_identity}
            {book_instruction}
            {memory_instruction}

            STUDENT PROFILE:
            - Student Name: {user_name}
            - Grade Level: {grade}
            - Study Field: {field}
            - Current Subject: {subject}
            - Preferred Language: {language}

            INSTRUCTIONS:
            1. Simplify: Explain like a kind older sibling.
            2. Localize: Use Ethiopian examples (The Blue Nile, Abyssinia, etc.).
            3. {language_logic}
            4. Structure: Use Markdown (bold, lists) for your UI.

            STUDENT QUESTION:
            "{user_message}"

            AI TUTOR RESPONSE:
            """

def build_validation_prompt(extracted_text, expected_subject, expected_grade, expected_language):
    """
    Asks the AI to verify if the PDF content matches the Study Room subject.
    """
    # We only send a sample to keep it fast
    sample = extracted_text[:6000] 
    
    return f"""
    You are an Ethiopian Academic Coordinator. 
    A student is trying to upload a document to a '{expected_subject}' Study Room for 'Grade {expected_grade}'.

    DOCUMENT CONTENT SAMPLE:
    \"\"\"{sample}\"\"\"

    TASK:
    1. SUBJECT MATCH: Is this content relevant to {expected_subject}?
    2. GRADE MATCH: Is the complexity level appropriate for Grade {expected_grade}? 
       (e.g., if the text is very basic addition but the room is Grade 12, it's a mismatch). and also is there any thing in the sample text which rexpress the grade lavel or subject.

    RETURN ONLY A JSON OBJECT:
    {{
        "is_match": true/false,
        "detected_subject": "Name of the actual subject",
        "detected_grade": "detected grade level",
        "feedback": "A short, helpful message in {expected_language} explaining why it was accepted or rejected."
    }}
    """
    
def build_topic_extraction_prompt(history_text):
    return f"""
    Based on the following study chat history, identify the ONE specific academic sub-topic 
    the student is currently learning. 
    Return ONLY the name of the topic (e.g., 'Photosynthesis', 'Linear Equations').
    
    CHAT HISTORY:
    {history_text}
    """

def build_quiz_generation_prompt(current_topic, text_slice, grade, subject):
    return f"""
    You are a Grade {grade} {subject} teacher.
    Create a 5-question MCQ quiz about '{current_topic}' based on the following text:
    
    TEXT CONTENT:
    {text_slice}
    
    REQUIREMENTS:
    - Format as a JSON list of objects ONLY.
    - Each object must include: id, question, options (A, B, C, D), answer, and explanation.
    - Keep the tone supportive and educational.

    JSON STRUCTURE:
    [
      {{
        "id": 1, 
        "question": "...", 
        "options": {{"A": "..", "B": "..", "C": "..", "D": ".."}}, 
        "answer": "A", 
        "explanation": "..."
      }}
    ]
    """
    
def build_summary_generation_prompt(current_topic, text_slice, grade, subject):
    return f"""
    You are an expert Grade {grade} {subject} tutor. 
    Provide a high-quality academic summary of '{current_topic}' based ONLY on the text provided below.
    
    TEXT CONTENT:
    {text_slice}
    
    FORMATTING REQUIREMENTS:
    1. SUMMARY: Provide 3-4 detailed paragraphs explaining the core concepts.
    2. KEY_TERMS: Identify 3-5 critical vocabulary terms and their definitions.
    
    OUTPUT STRUCTURE (Strict JSON):
    {{
      "topic": "{current_topic}",
      "summary_text": "...",
      "key_terms": [
        {{"term": "...", "definition": "..."}}
      ]
    }}
    """

