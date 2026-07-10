import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

app = Flask(__name__)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

conversation_history = [
    {
        "role": "system",
        "content": """You are an expert AI marketing 
assistant for Padsnap, a real estate technology 
company. You help real estate agents create 
professional, high-converting marketing content.

YOUR EXPERTISE:
- Writing compelling property listing descriptions
- Creating social media captions that drive engagement
- Crafting email subject lines that get opened
- Generating headlines that attract buyers

WHEN GIVEN PROPERTY DETAILS, ALWAYS respond 
in this EXACT structured format:

📋 HEADLINE:
(One powerful, attention-grabbing headline)

🏠 LISTING DESCRIPTION:
(2-3 professional paragraphs highlighting 
key features, lifestyle benefits, and 
unique selling points)

📱 INSTAGRAM CAPTION:
(Engaging, emoji-rich caption under 150 words)

📧 EMAIL SUBJECT LINE:
(5 different subject line options)

#️⃣ HASHTAGS:
(15 relevant real estate hashtags)

STYLE GUIDELINES:
- Use emotional, aspirational language
- Highlight lifestyle benefits not just features
- Create urgency without being pushy
- Always sound professional and trustworthy

Think step by step before writing.
First identify: property type, standout features,
target buyer, price positioning.
Then craft each section with that buyer in mind."""
    }
]

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")
    
    conversation_history.append({
        "role": "user",
        "content": user_message
    })
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=conversation_history
    )
    
    reply = response.choices[0].message.content
    
    conversation_history.append({
        "role": "assistant", 
        "content": reply
    })
    
    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(debug=True)