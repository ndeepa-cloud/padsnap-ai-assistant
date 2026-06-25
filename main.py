import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

client = Groq(api_key=api_key)

print("🤖 AI Assistant Ready! Type 'quit' to exit\n")

messages = []

while True:
    user_input = input("You: ")
    
    if user_input.lower() == "quit":
        print("Goodbye!")
        break
    
    messages.append({
        "role": "system",
        "content": "You are an expert AI assistant for Padsnap, a real estate technology company. Help real estate agents create professional property listings, marketing copy, and social media content. Always be professional, concise, and focused on real estate."
    }
    )
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages
    )
    
    reply = response.choices[0].message.content
    
    messages.append({
        "role": "assistant",
        "content": reply
    })
    
    print(f"\nAI: {reply}\n")