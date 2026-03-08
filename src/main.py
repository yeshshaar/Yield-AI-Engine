import os
import pandas as pd
import json
import time # Added for rate-limit safety
from groq import Groq 

from src.extractor import extract_text_from_pdf
from src.ai_parser import parse_resume_with_llama, parse_jd_with_llama
from src.scorer import calculate_skill_match
from src.sanitizer import clean_pii

def check_api():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("🚨 LOG ERROR: GROQ_API_KEY is missing from Streamlit Secrets!")
        return False
    return True

def process_resumes_to_csv(resume_folder, output_csv_path, jd_text_raw):
    print(f"--- 🚀 YIELD.AI PIPELINE START ---")
    
    if not check_api():
        return

    # Use absolute paths to avoid Linux directory confusion
    abs_resume_path = os.path.abspath(resume_folder)
    
    if not os.path.exists(abs_resume_path):
        print(f"🚨 LOG ERROR: {abs_resume_path} not found!")
        return
        
    files = [f for f in os.listdir(abs_resume_path) if f.lower().endswith(".pdf")]
    print(f"✅ LOG: Found {len(files)} files: {files}")

    if not files:
        print("🚨 LOG ERROR: No PDF files to process.")
        return

    # 1. Parse JD
    try:
        jd_skills = parse_jd_with_llama(jd_text_raw)
        print(f"✅ LOG: JD Extracted: {jd_skills}")
        time.sleep(1) # Brief pause to respect Groq rate limits
    except Exception as e:
        print(f"🚨 LOG ERROR: JD AI Failed! {e}")
        return 

    results = []
    
    # 2. Process Files
    for filename in files:
        pdf_path = os.path.join(abs_resume_path, filename)
        print(f"🔍 Analyzing: {filename}...")
        
        try:
            # Extraction & Sanitization
            raw_text = extract_text_from_pdf(pdf_path)
            if not raw_text:
                print(f"⚠️ Warning: Could not extract text from {filename}")
                continue
                
            sanitized_text = clean_pii(raw_text)
            
            # AI Parsing
            parsed_data = parse_resume_with_llama(sanitized_text)
            
            # Scoring
            candidate_skills = parsed_data.get("core_skills", []) + parsed_data.get("tools", [])
            match_score, matched, missing, improvement = calculate_skill_match(candidate_skills, jd_skills)
            
            results.append({
                "Candidate Name": parsed_data.get("name", "Unknown Candidate"),
                "Match Score (%)": int(match_score),
                "Matched Skills": ", ".join(matched) if matched else "None",
                "Missing Skills": ", ".join(missing) if missing else "None",
                "How to Improve": improvement,
                "Years of Experience": parsed_data.get("years_of_experience", 0),
                "Core Skills": ", ".join(parsed_data.get("core_skills", [])),
                "Tools": ", ".join(parsed_data.get("tools", [])),
                "Projects": ", ".join(parsed_data.get("projects", []))
            })
            print(f"✅ Successfully processed {filename}")
            time.sleep(1) # Safety gap between AI calls
            
        except Exception as e:
            print(f"🚨 LOG ERROR: Failed on {filename}: {e}")

    # 3. Final CSV Save
    if results:
        df = pd.DataFrame(results)
        
        # Sort by score so the best candidates are at the top
        df = df.sort_values(by="Match Score (%)", ascending=False)
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
        
        df.to_csv(output_csv_path, index=False)
        print(f"🏆 SUCCESS: Created CSV with {len(results)} results at {output_csv_path}")
    else:
        print("🚨 LOG ERROR: No results were generated.")