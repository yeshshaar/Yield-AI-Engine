import os
import pandas as pd
import json
from groq import Groq # Ensure this is imported

from src.extractor import extract_text_from_pdf
from src.ai_parser import parse_resume_with_llama, parse_jd_with_llama
from src.scorer import calculate_skill_match
from src.sanitizer import clean_pii

def check_api():
    """Diagnostic check to see if Groq is actually working in the cloud."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("🚨 LOG ERROR: GROQ_API_KEY is missing from Streamlit Secrets!")
        return False
    print(f"✅ LOG: API Key found (starts with {api_key[:6]}...)")
    return True

def process_resumes_to_csv(resume_folder, output_csv_path, jd_text_raw):
    print(f"--- DIAGNOSTIC PIPELINE START ---")
    
    if not check_api():
        return

    # Check the folder
    if not os.path.exists(resume_folder):
        print(f"🚨 LOG ERROR: {resume_folder} does not exist!")
        return
        
    files = [f for f in os.listdir(resume_folder) if f.lower().endswith(".pdf")]
    print(f"✅ LOG: Found {len(files)} files: {files}")

    try:
        jd_skills = parse_jd_with_llama(jd_text_raw)
        print(f"✅ LOG: JD Extracted: {jd_skills}")
    except Exception as e:
        print(f"🚨 LOG ERROR: JD AI Failed! Error: {e}")
        return # Stop here if JD fails

    results = []
    for filename in files:
        pdf_path = os.path.join(resume_folder, filename)
        print(f"Processing: {filename}")
        
        try:
            raw_text = extract_text_from_pdf(pdf_path)
            sanitized_text = clean_pii(raw_text)
            parsed_data = parse_resume_with_llama(sanitized_text)
            
            candidate_skills = parsed_data.get("core_skills", []) + parsed_data.get("tools", [])
            match_score, matched, missing, improvement = calculate_skill_match(candidate_skills, jd_skills)
            
            results.append({
                "Candidate Name": parsed_data.get("name", "Unknown"),
                "Match Score (%)": match_score,
                "Matched Skills": ", ".join(matched),
                "Missing Skills": ", ".join(missing),
                "How to Improve": improvement,
                "Years of Experience": parsed_data.get("years_of_experience", 0),
                "Core Skills": ", ".join(parsed_data.get("core_skills", [])),
                "Tools": ", ".join(parsed_data.get("tools", [])),
                "Projects": ", ".join(parsed_data.get("projects", []))
            })
        except Exception as e:
            print(f"🚨 LOG ERROR: Failed on {filename}: {e}")

    if results:
        pd.DataFrame(results).to_csv(output_csv_path, index=False)
        print(f"🏆 SUCCESS: CSV created at {output_csv_path}")
    else:
        print("🚨 LOG ERROR: Pipeline finished with 0 results.")