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
app.secret_key = os.getenv("SECRET_KEY")
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

    search_text = request.args.get("search", "")
    # this reads the rearch word form the query
    query = ChatHistory.query
    if search_text:
        query = query.filter(
            (ChatHistory.question.ilike(f"%{search_text}%")) | # OR
        #ilike means case-insensitive search.
            (ChatHistory.answer.ilike(f"%{search_text}%"))
        #question contains search text OR answer contains search text
        )

    if request.method == "POST":

        user_input = request.form.get("question", "").strip()
        subject = request.form.get("subject", "").strip()
        answer_style = request.form.get("answer_style", "").strip()

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
                model="MODEL_NAME",
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
    history = query.order_by(ChatHistory.created_at.desc()).all()
    #this is the name of DB / Start a database query on the ChatHistory table./ you know this  / Get all matching rows.

    return render_template("index.html", history=history, search_text=search_text)
#This sends the searched word to HTML.
# this is the end of home()

@app.route("/clear", methods=["POST"])
def clear_history():
    ChatHistory.query.delete()
    db.session.commit()
    return redirect("/")
@app.route("/delete/<int:history_id>", methods=["POST"])
def delete_history_item(history_id):
    item = ChatHistory.query.get_or_404(history_id)

    db.session.delete(item)
    db.session.commit()

    return redirect("/")


@app.route("/summarize", methods=["POST"])
def summarize_notes():
    notes = request.form["notes"]

    try:
        summary_prompt = f"""
You are an AI Study Assistant.

Summarize these notes for a student.

Return:
- Short summary
- Key points
- Important terms
- 3 quick quiz questions

Notes:
{notes}
"""

        ai_response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=summary_prompt
        )

        summary = ai_response.text

    except Exception as e:
        summary = "Sorry, I could not summarize the notes right now."

    history = ChatHistory.query.order_by(ChatHistory.created_at.desc()).all()

    return render_template(
        "index.html",
        history=history,
        summary=summary,
        search_text=""
    )


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=os.getenv("FLASK_DEBUG") == "1")