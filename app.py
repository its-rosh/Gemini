from flask import Flask, render_template, request
import google.generativeai as genai

# Gemini API Key
genai.configure(api_key="AIzaSyDUL-ObUYbhy0NVDijEY086fyRW4oansT8")

# Load Gemini model
model = genai.GenerativeModel("gemini-1.5-flash")

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():

    response = ""

    if request.method == "POST":

        user_input = request.form["question"]

        ai_response = model.generate_content(user_input)

        response = ai_response.text

    return render_template("index.html", response=response)

if __name__ == "__main__":
    app.run(debug=True)