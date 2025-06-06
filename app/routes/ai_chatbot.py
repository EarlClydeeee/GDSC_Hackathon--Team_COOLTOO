''' 
    This file defines a Flask route for a chatbot that answers legal questions 
'''


# --- Imports and environment setup ---
from flask import Flask, request, jsonify
from app import app
from flask import render_template
import requests
import os
from dotenv import load_dotenv
load_dotenv()


# --- Together.ai API configuration ---
TOGETHER_API_URL = "https://api.together.xyz/v1/chat/completions"
TOGETHER_MODEL = os.getenv("TOGETHER_MODEL")
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")

# --- Prompt template for the chatbot ---
BASE_PROMPT = """
You are a helpful legal assistant for a barangay in the Philippines. Answer questions clearly and politely based on local procedures, especially for issues like filing a blotter, paying fines, and requesting documents. Always advise users to consult the barangay hall or a lawyer for complex issues.

Question: {question}
Answer:
"""


# --- Route for the chatbot main page (renders the chat UI) ---
@app.route("/")
def chat():
    return render_template("ai_chatbot.html")

# --- Route for handling chatbot questions (GET renders UI, POST answers question) ---
@app.route("/ask", methods=["POST", "GET"])
@app.route("/ask/<path:question>", methods=["GET"])
@app.route("/ask", methods=["POST"])
def ask():
    # GET: Render the chat HTML page
    if request.method == "GET":
        return render_template("ai_chatbot.html")

    # POST: Handle the user's question sent as JSON
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 415
    data = request.get_json()
    question = data.get("question")
    if not question:
        return jsonify({"error": "Question is required."}), 400

    try:
        # Format the prompt for the LLM
        prompt = BASE_PROMPT.format(question=question)
        # Send the prompt to Together.ai API
        response = requests.post(
            TOGETHER_API_URL,
            headers={
                "Authorization": f"Bearer {TOGETHER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": TOGETHER_MODEL,
                "messages": [
                    {"role": "system", "content": "You are a barangay legal help bot."},
                    {"role": "user", "content": prompt}
                ]
            }
        )

        # Handle non-200 responses from the API
        if response.status_code != 200:
            return jsonify({"error": f"LLM error: {response.text}"}), 500

        # Extract and return the answer from the API response
        result = response.json()
        answer = result['choices'][0]['message']['content'].strip()
        return jsonify({"answer": answer})

    # Handle unexpected errors
    except Exception as e:
        return jsonify({"error": str(e)}), 500