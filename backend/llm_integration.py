import os
import requests
from sqlalchemy.orm import Session
from backend.models import EmissionHistory

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = os.getenv("GROQ_API_URL", "https://api.groq.com/openai/v1/chat/completions")  
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")  

def get_user_emissions(user_id: int, db: Session):
    """
    Fetch user-specific emissions history.
    """
    emissions = db.query(EmissionHistory).filter(
        EmissionHistory.user_id == user_id
    ).all()

    if not emissions:
        return "No emissions data available."

    # Summarize emissions data
    return "\n".join([
        f"{entry.category}: {entry.emission_value} kg CO2 (Miles: {entry.miles})"
        for entry in emissions
    ])

def chat_with_ai(user_id: int, user_query: str, db: Session):
    """
    Calls Groq AI for chatbot responses, integrating user emissions data.
    """
    # Fetch user emissions
    user_emissions = get_user_emissions(user_id, db)

    # ✅ Shorter, more specific prompt with user emissions context
    prompt = f"""
    You are an AI sustainability assistant. 
    **Be brief and give only 3 suggestions** based on the user's actual emissions data be very informative as well.

    **User Emissions Data:**
    {user_emissions}

    **User Query:** {user_query}

    Respond with **short, actionable steps** to reduce their carbon footprint in a very informative way.
    """

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": GROQ_MODEL,  
        "messages": [{"role": "system", "content": "Keep responses concise and directly related to sustainability."},
                     {"role": "user", "content": prompt}],
        "temperature": 0.5  # Lower temp = more focused response
    }

    response = requests.post(GROQ_API_URL, json=payload, headers=headers)
    response_data = response.json()

    if response.status_code == 200 and "choices" in response_data:
        return response_data["choices"][0]["message"]["content"]
    else:
        return f"Error: {response_data.get('error', 'Unknown error')}"
