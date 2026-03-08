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
    print("Extracting core skills from Job Description...")
    client = get_groq_client()
    
    prompt = f"""
    Extract the core skills from this Job Description. 
    Group interchangeable skills (like 'AWS or Azure') into one string.
    Return a JSON object with a 'skills' key.
    
    JD: {jd_text}
    """
    
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.1-8b-instant",
        response_format={"type": "json_object"}
    )
    
    # Wait 2 seconds to avoid hitting the Rate Limit on the next call
    time.sleep(2) 
    
    result = json.loads(response.choices[0].message.content)
    return result.get("skills", [])