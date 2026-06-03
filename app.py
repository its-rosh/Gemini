from flask import Flask, render_template, request, session
from google import genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

app = Flask(__name__)
app.secret_key = "study-assistant-secret"

@app.route("/", methods=["GET", "POST"])
def home():

    history = session.get("history", [])

    if request.method == "POST":

        user_input = request.form["question"]
        subject = request.form["subject"]
        answer_style = request.form["answer_style"]

        try:
            study_prompt = f"""
You are an AI Study Assistant.

Subject: {subject}
Answer style: {answer_style}

Your job:
- Explain concepts clearly
- Use simple student-friendly language
- Give step-by-step answers when requested
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

        history.append({
            "question": user_input,
            "answer": response,
            "subject": subject,
            "answer_style": answer_style
        })

        session["history"] = history

    return render_template("index.html", history=history)

if __name__ == "__main__":
    app.run(debug=True)