import plotly.graph_objects as go

def create_radar_chart(candidate_name, matched_skills, missing_skills):
    # 1. Catch the Pandas NaN (float) immediately and clear it
    if isinstance(matched_skills, float):
        matched_skills = ""
    if isinstance(missing_skills, float):
        missing_skills = ""
        
    # 2. Force everything into a string
    matched_str = str(matched_skills)
    missing_str = str(missing_skills)
    
    # 3. Safely split, completely ignoring "nan" strings or empties
    matched_list = matched_str.split(", ") if matched_str.lower() not in ["nan", "none", ""] else []
    missing_list = missing_str.split(", ") if missing_str.lower() not in ["nan", "none", ""] else []
    
    categories = ['Matched Skills Count', 'Missing Skills Count']
    r_values = [len(matched_list), len(missing_list)]
    
    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
          r=r_values,
          theta=categories,
          fill='toself',
          name=candidate_name,
          line_color='#00ffcc'
    ))

    fig.update_layout(
      polar=dict(
        radialaxis=dict(
          visible=True,
          range=[0, max(r_values) + 1] # Auto-scale based on data
        )
      ),
      showlegend=True,
      template="plotly_dark",
      title=f"📊 Skill Coverage Analysis: {candidate_name}"
    )
    
    return fig