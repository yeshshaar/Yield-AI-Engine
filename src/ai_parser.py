import os
import json
import time
from groq import Groq

def get_groq_client():
    """Ensures the key is pulled from the environment (Streamlit Secrets)."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is missing! Check Streamlit Secrets.")
    return Groq(api_key=api_key)

def parse_resume_with_llama(resume_text):
    print("Sending text to Llama 3 for analysis...")
    client = get_groq_client()
    
    prompt = f"""
    You are an AI resume parser. Extract the following information from the resume text into a JSON format:
    - name
    - years_of_experience (as a number)
    - core_skills (list of strings)
    - tools (list of strings)
    - projects (list of strings)
    
    Resume Text: {resume_text}
    """
    
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.1-8b-instant",
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)

def parse_jd_with_llama(jd_text):
    client = get_groq_client()
    # ... your prompt ...
    
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.1-8b-instant",
        response_format={"type": "json_object"}
    )
    
    data = json.loads(response.choices[0].message.content)
    skills = data.get("skills", [])
    
    # FIX: If the AI returns a string "Python, SQL", convert it to ["Python", "SQL"]
    if isinstance(skills, str):
        skills = [s.strip() for s in skills.split(",")]
    
    return skills