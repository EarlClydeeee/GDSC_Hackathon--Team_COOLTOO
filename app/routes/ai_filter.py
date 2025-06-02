import os
import google.generativeai as genai
from app.services import db, cursor
from datetime import date

AI_FILTER_MAX_CALLS = 500  # Daily limit

# Get the current usage count, and reset if it's a new day
def get_ai_filter_usage():
    cursor.execute("SELECT usage_count, last_reset FROM ai_filter_usage LIMIT 1")
    row = cursor.fetchone()
    if not row:
        # Initialize if not present
        cursor.execute("INSERT INTO ai_filter_usage (usage_count, last_reset) VALUES (0, %s)", (date.today(),))
        db.commit()
        return 0
    usage_count, last_reset = row
    # Reset counter if it's a new day
    if last_reset != date.today():
        cursor.execute("UPDATE ai_filter_usage SET usage_count = 0, last_reset = %s", (date.today(),))
        db.commit()
        return 0
    return usage_count

# Increment the AI filter usage count
def increment_ai_filter_usage():
    cursor.execute("UPDATE ai_filter_usage SET usage_count = usage_count + 1")
    db.commit()


# AI filter function to classify incident descriptions
def ai_filter(description):
    usage_count = get_ai_filter_usage()
    print(f"[AI FILTER] Usage count: {usage_count}/{AI_FILTER_MAX_CALLS}")
    if usage_count >= AI_FILTER_MAX_CALLS:
        print("[AI FILTER] Usage limit reached, returning 'common'")
        return "common"
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("[AI FILTER] GOOGLE_API_KEY not set, returning 'common'")
        return "common"
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("models/gemini-1.5-flash-latest")
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