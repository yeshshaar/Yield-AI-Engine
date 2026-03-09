import os
import pandas as pd
import json
import time 
import streamlit as st
from groq import Groq 
from src.database import save_evaluation
from src.extractor import extract_text_from_file
from src.ai_parser import parse_resume_with_llama, parse_jd_with_llama
from src.scorer import calculate_skill_match
from src.sanitizer import clean_pii

# --- 1. INITIALIZE GROQ SAFELY ---
try:
    API_KEY = st.secrets["GROQ_API_KEY"]
except (FileNotFoundError, KeyError):
    API_KEY = os.environ.get("GROQ_API_KEY")

if API_KEY:
    client = Groq(api_key=API_KEY)
else:
    print("🚨 ERROR: GROQ_API_KEY is missing!")
    client = None

# --- 2. CORE FUNCTIONS ---
def evaluate_with_llama(resume_text, jd_text):
    """Sends the prompt to Groq and forces a JSON response."""
    if not client:
        return None

    system_prompt = """
    You are an expert Technical Recruiter evaluating a resume against a Job Description.
    You must analyze the candidate and return strictly a JSON object. Do not include any markdown formatting or extra text outside the JSON.
    
    Format:
    {
      "skill_match_score": 70, 
      "semantic_match_score": 85,
      "experience_relevance_score": 78,
      "matched_skills": ["Skill1", "Skill2"],
      "missing_skills": ["Skill3", "Skill4"]
    }
    """
    user_prompt = f"Job Description:\n{jd_text}\n\nCandidate Resume:\n{resume_text}"

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"}, 
            temperature=0.2 
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"API Error: {e}")
        return None

def process_evaluation(llm_json_response):
    """Parses the JSON and calculates the Yield-AI weighted score."""
    if not llm_json_response:
        return None
        
    # Clean rogue markdown just in case the AI wraps it in ```json
    cleaned_response = llm_json_response.replace("```json", "").replace("```", "").strip()
    
    try:
        data = json.loads(cleaned_response)
    except Exception as e:
        print(f"JSON Parsing Error: {e}")
        return None 
        
    s_skill = data.get("skill_match_score", 0)
    s_semantic = data.get("semantic_match_score", 0)
    s_exp = data.get("experience_relevance_score", 0)
    
    # Apply the 40/35/25 weights
    overall_score = round((s_skill * 0.40) + (s_semantic * 0.35) + (s_exp * 0.25), 1)
    
    return {
        "overall_score": overall_score,
        "breakdown": {
            "Skill Match": s_skill,
            "Semantic Match": s_semantic,
            "Experience Relevance": s_exp
        },
        "matched_skills": data.get("matched_skills", []),
        "missing_skills": data.get("missing_skills", [])
    }

def process_resumes_to_csv(raw_dir, output_csv, jd_text, progress_callback=None):
    """
    Reads PDFs, scores them using the Yield-AI weighted engine, 
    and saves the detailed breakdown to a CSV for the UI.
    """
    results = []
    files = [f for f in os.listdir(raw_dir) if f.lower().endswith(('.pdf', '.docx'))]
    total_files = len(files)

    for i, filename in enumerate(files):
        filepath = os.path.join(raw_dir, filename)
        candidate_name = filename.replace(".pdf", "").replace("_", " ")
        
        # 1. 📂 Extract Text from PDF (Fixed the hardcoded placeholder!)
        try:
            resume_text = extract_text_from_file(filepath) 
        except Exception as e:
            print(f"PDF Extraction Error on {filename}: {e}")
            resume_text = ""
        
        # 2. 🧠 Call the Groq Engine
        raw_json_result = evaluate_with_llama(resume_text, jd_text)
        
        # 3. 🧮 Process the Math
        if raw_json_result:
            parsed_data = process_evaluation(raw_json_result)
        else:
            parsed_data = None

        # Fallback if API fails or parsing breaks
        if not parsed_data:
            parsed_data = {
                "overall_score": 0,
                "breakdown": {"Skill Match": 0, "Semantic Match": 0, "Experience Relevance": 0},
                "matched_skills": [],
                "missing_skills": []
            }

        # 4. 📊 Map to UI Columns
        results.append({
            "Candidate Name": candidate_name,
            "Score": parsed_data["overall_score"],
            "Skill Match": parsed_data["breakdown"]["Skill Match"],
            "Semantic Match": parsed_data["breakdown"]["Semantic Match"],
            "Experience Relevance": parsed_data["breakdown"]["Experience Relevance"],
            "Matched Skills": ", ".join(parsed_data["matched_skills"]),
            "Missing Skills": ", ".join(parsed_data["missing_skills"])
        })

        if progress_callback:
            progress_callback(i, total_files, filename)

    # 5. 💾 Save to CSV
    df = pd.DataFrame(results)
    if not df.empty:
        df = df.sort_values(by="Score", ascending=False)
    df.to_csv(output_csv, index=False)
    
    return df