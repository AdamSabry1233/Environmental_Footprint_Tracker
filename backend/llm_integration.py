import os
import requests
from sqlalchemy.orm import Session
from backend.models import EmissionHistory

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = os.getenv("GROQ_API_URL", "https://api.groq.com/openai/v1/chat/completions")  
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")  

def get_user_emissions(user_id: int, db: Session):
    emissions = db.query(EmissionHistory).filter(EmissionHistory.user_id == user_id).all()
    if not emissions:
        return "No emissions data available."
    
    return "\n".join([f"{entry.category}: {entry.emission_value} kg CO2" for entry in emissions])

def chat_with_ai(user_id: int, user_query: str, db: Session):
    user_emissions = get_user_emissions(user_id, db)

    prompt = f"""
    You are an AI sustainability assistant. 
    **Your role**: Give short, helpful eco-friendly advice in a conversational way.

    - Be **engaging but brief** (limit to 2-3 sentences).
    - Always ask a **follow-up question** to keep the conversation flowing.
    - Offer **choices** to guide users to their next topic.
    - Assume CO2 emissions are always in IBs
    
    --- 
    **User Data:** {user_emissions}
    **User Query:** {user_query}
    ---

    Keep it short.
    Ask a follow-up question.
    Offer 2-3 topic choices.
    - Make sure concrete answers are provided if a follow up question is asked.
    """

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": GROQ_MODEL,  
        "messages": [
            {"role": "system", "content": "Keep responses concise and interactive."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }

    response = requests.post(GROQ_API_URL, json=payload, headers=headers)
    response_data = response.json()

    if response.status_code == 200 and "choices" in response_data:
        return response_data["choices"][0]["message"]["content"]
    else:
        return f"Error: {response_data.get('error', 'Unknown error')}"
