import os
import pandas as pd
import json

from src.extractor import extract_text_from_pdf
from src.ai_parser import parse_resume_with_llama, parse_jd_with_llama
from src.scorer import calculate_skill_match
from src.sanitizer import clean_pii

def process_resumes_to_csv(resume_folder, output_csv_path, jd_text_raw):
    """Orchestrates the pipeline with deep logging for debugging."""
    print(f"--- PIPELINE START ---")
    print(f"Checking folder: {os.path.abspath(resume_folder)}")
    
    # 1. Check if the folder even exists and what is inside it
    if not os.path.exists(resume_folder):
        print(f"🚨 ERROR: Folder {resume_folder} does not exist!")
        return
    
    files_in_dir = os.listdir(resume_folder)
    print(f"Files found in {resume_folder}: {files_in_dir}")

    # 2. Parse the JD
    try:
        jd_skills = parse_jd_with_llama(jd_text_raw)
        print(f"Target JD Skills: {jd_skills}")
    except Exception as e:
        print(f"🚨 JD Extraction Failed: {e}")
        raise e

    results = []
    
    # 3. Process each file
    for filename in files_in_dir:
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(resume_folder, filename)
            print(f"Processing file: {pdf_path}")
            
            try:
                # Extraction
                raw_text = extract_text_from_pdf(pdf_path)
                if not raw_text:
                    print(f"⚠️ Warning: No text found in {filename}")
                    continue
                
                # Sanitization
                sanitized_text = clean_pii(raw_text)
                
                # AI Parsing
                parsed_data = parse_resume_with_llama(sanitized_text)
                
                # Scoring
                candidate_skills = parsed_data.get("core_skills", []) + parsed_data.get("tools", [])
                match_score, matched, missing, improvement = calculate_skill_match(candidate_skills, jd_skills)
                
                record = {
                    "Candidate Name": parsed_data.get("name", "Unknown"),
                    "Match Score (%)": match_score,
                    "Matched Skills": ", ".join(matched),
                    "Missing Skills": ", ".join(missing),
                    "How to Improve": improvement,
                    "Years of Experience": parsed_data.get("years_of_experience", 0),
                    "Core Skills": ", ".join(parsed_data.get("core_skills", [])),
                    "Tools": ", ".join(parsed_data.get("tools", [])),
                    "Projects": ", ".join(parsed_data.get("projects", []))
                }
                results.append(record)
                print(f"✅ Successfully evaluated {filename}")
                
            except Exception as e:
                print(f"🚨 CRASH while processing {filename}: {e}")
                raise e
                
    # 4. Save to CSV
    if results:
        df = pd.DataFrame(results)
        df = df.sort_values(by="Match Score (%)", ascending=False) 
        df.to_csv(output_csv_path, index=False)
        print(f"SUCCESS: Created CSV at {output_csv_path}")
    else:
        print("🚨 PIPELINE ENDED: No results generated. Loop finished without matches.")