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
        "content": """You are an expert AI assistant 
for Padsnap, a real estate technology company. 
Your job is to help real estate agents create:
- Professional property listing descriptions
- Social media captions for properties  
- Email marketing copy
- Compelling headlines for listings
Always be professional and focused on 
real estate marketing."""
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