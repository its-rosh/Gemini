from flask import Flask, render_template, request
from google import genai

# Create Gemini client
client = genai.Client(api_key="AIzaSyBHVyJsjoV-LI2QoHKKiER4Jx49DmxE1sk")

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():

    response = ""

    if request.method == "POST":

        user_input = request.form["question"]

        # Send request to Gemini
        ai_response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=user_input
        )

        response = ai_response.text

    return render_template("index.html", response=response)

if __name__ == "__main__":
    app.run(debug=True)