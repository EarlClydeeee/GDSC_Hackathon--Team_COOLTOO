"""
    This module provides an AI filter to classify incident descriptions
    as either 'urgent' or 'common' using Google Generative AI.
"""


# --- Imports and environment setup ---
import os
import google.generativeai as genai
from app.services import connect_to_db
from datetime import date


# --- Configuration: Daily usage limit for the AI filter ---
AI_FILTER_MAX_CALLS = 500  # Daily limit

# --- Usage Counter: Get current usage count, reset if it's a new day ---
def get_ai_filter_usage():
    db, cursor = connect_to_db()
    cursor.execute("SELECT usage_count, last_reset FROM ai_filter_usage LIMIT 1")
    row = cursor.fetchone()
    if not row:
        # Initialize usage counter if not present
        cursor.execute("INSERT INTO ai_filter_usage (usage_count, last_reset) VALUES (0, %s)", (date.today(),))
        db.commit()
        return 0
    usage_count, last_reset = row
    # Reset counter if it's a new day
    if last_reset != date.today():
        cursor.execute("UPDATE ai_filter_usage SET usage_count = 0, last_reset = %s", (date.today(),))
        db.commit()
        return 0
    cursor.close()
    db.close()
    return usage_count

# --- Usage Counter: Increment the AI filter usage count ---
def increment_ai_filter_usage():
    db, cursor = connect_to_db()
    cursor.execute("UPDATE ai_filter_usage SET usage_count = usage_count + 1")
    db.commit()

    cursor.close()
    db.close()


# --- AI Filter: Classify incident descriptions as 'urgent' or 'common' ---
def ai_filter(description):
    usage_count = get_ai_filter_usage()
    print(f"[AI FILTER] Usage count: {usage_count}/{AI_FILTER_MAX_CALLS}")
    if usage_count >= AI_FILTER_MAX_CALLS:
        print("[AI FILTER] Usage limit reached, returning 'common'")
        return "common"
    
    # Get API key from environment
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("[AI FILTER] GOOGLE_API_KEY not set, returning 'common'")
        return "common"
    
    # Configure Gemini model
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("models/gemini-1.5-flash-latest")

    # Build prompt with clear instructions and examples
    prompt = (
        "You are an assistant that classifies incident reports for a local government.\n"
        "Classify the following incident description as either 'urgent' or 'common'.\n"
        "'Urgent' means the situation requires immediate government attention (threats to life, major accidents, disasters, violence, emergencies).\n"
        "'Common' means it is a routine, non-emergency, or minor issue.\n"
        "Respond with ONLY 'urgent' or 'common'. Do not explain your answer.\n"
        "\n"
        "Examples:\n"
        "Description: There is a fire in my neighbor's house and people are trapped inside.\n"
        "Label: urgent\n"
        "Description: The streetlight on 5th avenue is broken.\n"
        "Label: common\n"
        "Description: I witnessed a robbery at the corner store.\n"
        "Label: urgent\n"
        "Description: There is a pothole on Main Street.\n"
        "Label: common\n"
        "\n"
        f"Description: {description}\n"
        "Label:"
    )
    print(f"[AI FILTER] Prompt sent to Gemini:\n{prompt}\n")

    # Call Gemini API and handle response
    try:
        response = model.generate_content(prompt)
        increment_ai_filter_usage()
        result = response.text.strip().lower()
        print(f"[AI FILTER] Raw AI response: {repr(response.text)}")
        print(f"[AI FILTER] Parsed result: {result}")
        if "urgent" in result:
            print("[AI FILTER] Classified as URGENT")
            return "urgent"
        print("[AI FILTER] Classified as COMMON")
        return "common"
    except Exception as e:
        print(f"[AI FILTER] Exception: {e}")
        return "common"