import os
import json
from flask import Flask, render_template, request, jsonify, Response, stream_with_context
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
app = Flask(__name__)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """You are Padsnap AI, an expert
real estate assistant. You help users find properties
and create professional marketing content.

When generating marketing content ALWAYS use this format:

📋 HEADLINE:
(One powerful headline)

🏠 LISTING DESCRIPTION:
(2-3 professional paragraphs)

📱 INSTAGRAM CAPTION:
(Engaging caption under 150 words)

📧 EMAIL SUBJECT LINES:
1. (option 1)
2. (option 2)
3. (option 3)
4. (option 4)
5. (option 5)

#️⃣ HASHTAGS:
(15 relevant hashtags)"""

SEARCH_KEYWORDS = [
    # Actions
    'find', 'search', 'looking', 'need', 'want',
    'show', 'buy', 'get', 'rent', 'lease',
    # Property types
    'bed', 'bath', 'bedroom', 'bathroom',
    'house', 'home', 'condo', 'apartment',
    'studio', 'townhouse', 'penthouse', 'villa',
    'ranch', 'cottage', 'duplex', 'loft',
    'property', 'properties', 'listing', 'listings',
    'real estate', 'realty',
    # Price indicators
    '$', 'million', 'thousand', 'price', 'budget',
    'under', 'below', 'above', 'around', 'cheap',
    'affordable', 'luxury', 'expensive',
    # Features
    'pool', 'garage', 'garden', 'backyard', 'yard',
    'parking', 'balcony', 'view', 'modern',
    'renovated', 'new', 'spacious', 'cozy',
    # US Cities
    'austin', 'new york', 'nyc', 'manhattan',
    'brooklyn', 'bronx', 'queens', 'miami',
    'chicago', 'los angeles', 'la', 'san francisco',
    'sf', 'seattle', 'denver', 'atlanta', 'dallas',
    'houston', 'phoenix', 'vegas', 'las vegas',
    'boston', 'washington', 'dc', 'nashville',
    'portland', 'san diego', 'orlando', 'tampa',
    'charlotte', 'raleigh', 'minneapolis',
    'detroit', 'philadelphia', 'philly',
    'baltimore', 'pittsburgh', 'cleveland',
    'columbus', 'indianapolis', 'memphis',
    'louisville', 'richmond', 'salt lake',
    'sacramento', 'fresno', 'tucson', 'mesa',
    'omaha', 'kansas city', 'tulsa',
    # US States
    'florida', 'california', 'texas', 'new york',
    'illinois', 'washington', 'georgia', 'ohio',
    'north carolina', 'michigan', 'arizona',
    'colorado', 'tennessee', 'oregon', 'nevada',
    'kentucky', 'virginia', 'indiana', 'maryland',
    # International
    'london', 'toronto', 'sydney', 'dubai',
    # Location descriptors
    'downtown', 'suburb', 'suburban', 'rural',
    'urban', 'neighborhood', 'area', 'district',
    'near', 'close', 'walk', 'commute',
    'school', 'beach', 'ocean', 'lake', 'mountain',
    # Other
    'sale', 'for sale', 'available', 'invest',
    'investment', 'flip', 'agent', 'realtor',
    'broker', 'sqft', 'square feet', 'acres',
    'family', 'single family', 'starter',
    'move in', 'murray', 'ky', 'kentucky'
]


def is_property_search(message):
    msg = message.lower()
    if any(kw in msg for kw in SEARCH_KEYWORDS):
        return True
    try:
        detect = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{
                "role": "user",
                "content": f"""Is this message asking to find or search 
for real estate properties or homes?
Message: "{message}"
Answer only YES or NO."""
            }],
            max_tokens=3,
            temperature=0
        )
        return "YES" in detect.choices[0].message.content.upper()
    except:
        return False


def generate_properties(query):
    prompt = f"""Generate exactly 4 realistic property
listings based on this search query: "{query}"

Return ONLY a valid JSON object:
{{
  "summary": "brief one line description of search",
  "properties": [
    {{
      "id": 1,
      "address": "123 Oak Street",
      "city": "Austin",
      "state": "TX",
      "price": "$485,000",
      "beds": 3,
      "baths": 2,
      "sqft": "1,850",
      "features": ["Pool", "Modern Kitchen", "Backyard"],
      "type": "Single Family Home",
      "status": "For Sale"
    }},
    {{
      "id": 2,
      "address": "456 Elm Avenue",
      "city": "Austin",
      "state": "TX",
      "price": "$465,000",
      "beds": 3,
      "baths": 2,
      "sqft": "1,720",
      "features": ["Garden", "Open Floor Plan", "New Roof"],
      "type": "Single Family Home",
      "status": "For Sale"
    }},
    {{
      "id": 3,
      "address": "789 Maple Drive",
      "city": "Austin",
      "state": "TX",
      "price": "$499,000",
      "beds": 4,
      "baths": 3,
      "sqft": "2,100",
      "features": ["Modern Kitchen", "2 Car Garage", "Master Suite"],
      "type": "Single Family Home",
      "status": "For Sale"
    }},
    {{
      "id": 4,
      "address": "321 Pine Street",
      "city": "Austin",
      "state": "TX",
      "price": "$425,000",
      "beds": 3,
      "baths": 1,
      "sqft": "1,550",
      "features": ["Renovated", "Hardwood Floors", "Big Backyard"],
      "type": "Single Family Home",
      "status": "For Sale"
    }}
  ]
}}

IMPORTANT RULES:
- Use the EXACT city and state from the search query
- Use the EXACT price range from the search query
- Match the property type from the search query
- Make all 4 properties different addresses
- Return ONLY valid JSON nothing else"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=2000
    )

    raw = response.choices[0].message.content.strip()
    start = raw.find('{')
    end = raw.rfind('}') + 1
    if start != -1 and end != 0:
        raw = raw[start:end]

    try:
        data = json.loads(raw)
        return data
    except:
        return {"summary": "", "properties": []}


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    message = request.json.get("message", "")
    history = request.json.get("history", [])

    if is_property_search(message):
        data = generate_properties(message)
        props = data.get("properties", [])
        count = len(props)

        if count > 0:
            reply = (
                f"I found {count} properties matching your search! "
                f"Click any property card on the left to generate "
                f"professional marketing content instantly."
            )
        else:
            reply = (
                "I couldn't find properties for that search. "
                "Try something like '3 bed house in Austin under $500K' "
                "or 'luxury condo in Miami'"
            )

        return jsonify({
            "type": "search",
            "properties": props,
            "message": reply
        })

    else:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages += history
        messages.append({"role": "user", "content": message})

        def stream():
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                temperature=0.7,
                max_tokens=2000,
                stream=True
            )
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        return Response(
            stream_with_context(stream()),
            mimetype='text/plain'
        )


@app.route("/generate", methods=["POST"])
def generate():
    property_data = request.json.get("property", {})

    prompt = f"""Generate complete marketing content
for this property:

Address: {property_data.get('address')}, {property_data.get('city')}, {property_data.get('state')}
Price: {property_data.get('price')}
Bedrooms: {property_data.get('beds')}
Bathrooms: {property_data.get('baths')}
Size: {property_data.get('sqft')} sqft
Type: {property_data.get('type')}
Features: {', '.join(property_data.get('features', []))}

Generate the headline, listing description,
Instagram caption, email subject lines, and hashtags."""

    def stream():
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000,
            stream=True
        )
        for chunk in completion:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    return Response(
        stream_with_context(stream()),
        mimetype='text/plain'
    )


if __name__ == "__main__":
    app.run(debug=True)