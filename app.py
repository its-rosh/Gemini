from flask import Flask, render_template, request
from google import genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Create Gemini client
client = genai.Client(api_key=api_key)

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():

    response = ""
    question = ""

    if request.method == "POST":

        user_input = request.form["question"]
        subject = request.form["subject"]
        question = user_input

        try:
            study_prompt = f"""
You are an AI Study Assistant.

Subject: {subject}

Your job:
- Explain concepts clearly
- Use simple student-friendly language
- Give step-by-step answers
- Use examples when helpful
- If the student asks for homework help, explain the method first


Student question:
{user_input}
"""

            ai_response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=study_prompt
            )

            response = ai_response.text

        except Exception as e:
            response = "Sorry, something went wrong. Please try again after a few minutes."

    return render_template("index.html", response=response,  question=question)

if __name__ == "__main__":
    app.run(debug=True)