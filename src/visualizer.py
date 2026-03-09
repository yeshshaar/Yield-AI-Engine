import plotly.graph_objects as go

def create_radar_chart(candidate_name, matched_skills, missing_skills):
    # 1. Safely handle Pandas NaNs (floats)
    if isinstance(matched_skills, float):
        matched_skills = ""
    if isinstance(missing_skills, float):
        missing_skills = ""
        
    # 2. Force to string
    matched_str = str(matched_skills)
    missing_str = str(missing_skills)
    
    # 3. Clean split
    matched_list = matched_str.split(", ") if matched_str.lower() not in ["nan", "none", ""] else []
    missing_list = missing_str.split(", ") if missing_str.lower() not in ["nan", "none", ""] else []
    
    categories = ['Matched Skills', 'Missing Skills']
    r_values = [len(matched_list), len(missing_list)]
    
    fig = go.Figure()

    # --- THE TRACE (The Neon Polygon) ---
    fig.add_trace(go.Scatterpolar(
          r=r_values,
          theta=categories,
          fill='toself',
          fillcolor='rgba(0, 255, 204, 0.2)', # Glassmorphism neon cyan fill
          line=dict(color='#00ffcc', width=3), # Solid neon cyan border
          marker=dict(color='#00ffcc', size=8), # Glowing dots at the edges
          name=candidate_name
    ))

    # --- THE LAYOUT (The Dark Theme Overrides) ---
    fig.update_layout(
      polar=dict(
        bgcolor='rgba(10, 12, 30, 0.4)', # Deep space-navy background inside the radar
        radialaxis=dict(
          visible=True,
          range=[0, max(max(r_values) + 1, 5)], # Forces a minimum scale so it doesn't look distorted
          gridcolor='rgba(138, 43, 226, 0.3)', # Deep Purple web lines
          linecolor='rgba(138, 43, 226, 0.5)', 
          tickfont=dict(color='#8a8d9e') # Subtle grey numbers
        ),
        angularaxis=dict(
          gridcolor='rgba(138, 43, 226, 0.3)', # Deep Purple outer ring
          linecolor='rgba(138, 43, 226, 0.5)',
          tickfont=dict(color='#00ffcc', size=14, weight="bold") # Cyan labels
        )
      ),
      paper_bgcolor='rgba(0,0,0,0)', # Makes the outer square totally invisible!
      plot_bgcolor='rgba(0,0,0,0)',
      showlegend=False,
      title=dict(
          text=f"📊 Skill Coverage Analysis: {candidate_name}",
          font=dict(color='#ffffff', size=20)
      ),
      margin=dict(t=60, b=40, l=40, r=40)
    )
    
    return fig