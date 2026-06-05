from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from google import genai
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
database_url = os.getenv("DATABASE_URL")

client = genai.Client(api_key=api_key)

app = Flask(__name__)
app.secret_key = "study-assistant-secret"
app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class ChatHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    subject = db.Column(db.String(50), nullable=False)
    answer_style = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@app.route("/", methods=["GET", "POST"])
def home():

    history = ChatHistory.query.order_by(ChatHistory.created_at.desc()).all()

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

        chat = ChatHistory(
        question=user_input,
        answer=response,
        subject=subject,
        answer_style=answer_style)

        db.session.add(chat)
        db.session.commit()
        history = ChatHistory.query.order_by(ChatHistory.created_at.desc()).all()

    return render_template("index.html", history=history)

@app.route("/clear", methods=["POST"])
def clear_history():
    ChatHistory.query.delete()
    db.session.commit()
    return redirect("/")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)