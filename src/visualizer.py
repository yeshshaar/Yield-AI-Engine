import plotly.graph_objects as go

def create_radar_chart(candidate_name, matched_skills, missing_skills):
    # Split the strings back into lists for counting
    matched_list = matched_skills.split(", ") if matched_skills != "None" else []
    missing_list = missing_skills.split(", ") if missing_skills != "None" else []
    
    # We define the counts for the radar axes
    # We use counts to show the 'volume' of expertise vs gaps
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