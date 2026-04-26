import streamlit as st
import json

st.set_page_config(page_title="SkillScan AI", page_icon="🎯", layout="wide", initial_sidebar_state="collapsed")

with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def call_claude(system_prompt: str, user_message: str, max_tokens: int = 3000) -> str:
    api_key = st.session_state.get("api_key", "")
    if not api_key:
        return "Error: No API key."
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash-lite",
            system_instruction=system_prompt
        )
        response = model.generate_content(user_message)
        return response.text
    except Exception as e:
        st.error(f"Exact error: {str(e)}")
        return ""

def parse_json(text: str) -> dict:
    try:
        clean = text.strip().replace("```json", "").replace("```", "").strip()
        return json.loads(clean)
    except:
        return {}

def color_for_score(score):
    if score >= 7: return "#22c55e"
    if score >= 4: return "#f59e0b"
    return "#ef4444"

def badge_for_priority(priority):
    return {"High": "#ef4444", "Medium": "#f59e0b", "Low": "#22c55e"}.get(priority, "#6b7280")

def render_step_indicator(current_step):
    steps = ["Input", "Skill Map", "Assessment", "Dashboard"]
    cols = st.columns(len(steps))
    for i, (col, step) in enumerate(zip(cols, steps)):
        n = i + 1
        status = "done" if n < current_step else "active" if n == current_step else "pending"
        icon = "✓" if status == "done" else str(n)
        col.markdown(f'<div class="step-item {status}"><div class="step-circle">{icon}</div><div class="step-label">{step}</div></div>', unsafe_allow_html=True)

# ── IMPROVEMENT 1: SKILL DECOMPOSITION ──────────────────────────────────────
def decompose_skills(jd_text: str, resume_text: str) -> dict:
    system = """You are an expert technical skills analyst.
For each key skill in the JD, decompose into 4 capability layers and assess the candidate.
Return ONLY valid JSON. No markdown. No explanation.
{
  "role_title": "Job Title",
  "candidate_name": "Name or Candidate",
  "overall_match_percent": 55,
  "skills": [
    {
      "name": "Python",
      "layers": {
        "syntax": {"description": "loops, functions, data types", "jd_needs": true, "candidate_has": true},
        "applied": {"description": "file handling, APIs, libraries", "jd_needs": true, "candidate_has": false},
        "problem_solving": {"description": "DSA, algorithms, logic", "jd_needs": false, "candidate_has": false},
        "real_world": {"description": "debugging, optimization, production", "jd_needs": true, "candidate_has": false}
      },
      "claimed_level": "Syntax",
      "required_level": "Applied + Real-world",
      "gap_summary": "You know Python at syntax level, but role needs API integration and debugging",
      "priority": "High"
    }
  ],
  "strong_areas": ["skill1"],
  "weak_areas": ["skill1"]
}"""
    result = call_claude(system, f"JD:\n{jd_text}\n\nResume:\n{resume_text}", max_tokens=4000)
    return parse_json(result)

# ── IMPROVEMENT 2: CONVERSATIONAL SCENARIO QUESTIONS ────────────────────────
def generate_scenario_question(skill: str, layer: str, question_num: int, conversation_history: list) -> str:
    history_text = ""
    if conversation_history:
        history_text = "Conversation so far:\n" + "\n".join(
            [f"{'AI' if m['role']=='ai' else 'Candidate'}: {m['content']}" for m in conversation_history[-4:]]
        )
    system = """You are a senior technical interviewer. Ask scenario-based questions that reveal real thinking.
- Q1: Real-world scenario requiring this skill. Ask how they'd approach it.
- Q2: Follow-up "why?" or edge case variation based on their answer.
- Q3: Harder scenario — scale, failure, or optimization challenge.
Rules: Sound conversational. Never ask definitions. Always give context ("Suppose you have 1M records..."). One question only."""
    prompt = f"Skill: {skill}\nLayer focus: {layer}\nQuestion number: {question_num} of 3\n{history_text}\nAsk question {question_num}:"
    return call_claude(system, prompt, max_tokens=300)

# ── IMPROVEMENT 3: CONFIDENCE + EVIDENCE SCORING ────────────────────────────
def score_with_evidence(skill: str, layers: dict, conversation: list) -> dict:
    qa_text = "\n".join([f"{'AI' if m['role']=='ai' else 'Candidate'}: {m['content']}" for m in conversation])
    system = """Score the candidate with confidence level and specific evidence.
Return ONLY valid JSON:
{
  "score": 6,
  "level": "Intermediate",
  "confidence_percent": 72,
  "evidence": {
    "strengths": ["specific thing they showed"],
    "gaps": ["specific thing they missed"],
    "reasoning": "one sentence"
  },
  "layer_scores": {"syntax": 8, "applied": 5, "problem_solving": 4, "real_world": 3},
  "verdict": "Python: Intermediate (Confidence: 72%) — Gap: lacks real-world debugging experience"
}"""
    result = call_claude(system, f"Skill: {skill}\nLayers: {json.dumps(layers)}\nConversation:\n{qa_text}", max_tokens=800)
    data = parse_json(result)
    if not data:
        data = {"score": 5, "level": "Intermediate", "confidence_percent": 60,
                "evidence": {"strengths": [], "gaps": [], "reasoning": "Assessment completed"},
                "layer_scores": {"syntax": 5, "applied": 5, "problem_solving": 5, "real_world": 5},
                "verdict": f"{skill}: Assessment completed"}
    return data

# ── IMPROVEMENT 4: ADJACENT SKILL MAPPING ───────────────────────────────────
def map_adjacent_skills(skill_scores: dict, decomposed: dict) -> dict:
    system = """You are a career learning strategist. Suggest adjacent, achievable upgrade paths.
Return ONLY valid JSON:
{
  "gap_maps": [
    {
      "target_skill": "Machine Learning",
      "candidate_knows": "Python + basic stats",
      "jd_needs": "ML model building",
      "adjacent_path": ["Step 1 (builds on what they know)", "Step 2", "Step 3"],
      "avoid_jumping_to": "Deep Learning (too far from current level)",
      "realistic_weeks": 6
    }
  ]
}"""
    weak = {s: d for s, d in skill_scores.items() if d.get("score", 10) < 7}
    result = call_claude(system, f"Scores: {json.dumps(weak)}\nSkills: {json.dumps(decomposed.get('skills',[]))}", max_tokens=2000)
    return parse_json(result)

# ── IMPROVEMENT 5+6: PERSONALISED PLAN WITH TIME REALISM ────────────────────
def generate_learning_plan(skill_scores: dict, adjacent_maps: dict, decomposed: dict) -> dict:
    system = """Create a realistic personalised learning plan. Time estimates based on current level:
- Beginner to Intermediate: 4-6 weeks. Intermediate to Proficient: 2-3 weeks.
Each skill needs: 1 beginner resource, 1 hands-on resource, 1 project with mini-task.
Return ONLY valid JSON:
{
  "overall_readiness": "62%",
  "time_to_job_ready": "2.5 months",
  "weekly_schedule": [{"week_range": "Week 1-2", "focus": "Python APIs", "daily_hours": 2}],
  "skill_plans": [
    {
      "skill": "Python API development",
      "why_needed": "Required for backend role",
      "current_level": "Syntax", "target_level": "Applied",
      "weeks": 2, "difficulty": "Medium", "daily_hours": 2,
      "resources": [
        {"type": "Beginner", "title": "Resource name", "url": "https://...", "duration": "3 hours"},
        {"type": "Hands-on", "title": "Resource name", "url": "https://...", "duration": "5 hours"},
        {"type": "Project", "title": "Project name", "url": "https://...", "duration": "6 hours"}
      ],
      "mini_task": "Build a REST API for student records"
    }
  ],
  "motivational_note": "Specific encouraging note"
}"""
    weak = {s: d for s, d in skill_scores.items() if d.get("score", 10) < 7}
    result = call_claude(system, f"Scores: {json.dumps(weak)}\nAdjacent: {json.dumps(adjacent_maps)}\nRole: {decomposed.get('role_title','')}", max_tokens=4000)
    data = parse_json(result)
    if not data:
        data = {"overall_readiness": "50%", "time_to_job_ready": "3 months",
                "weekly_schedule": [], "skill_plans": [], "motivational_note": "Keep going!"}
    return data

# ═══════════════════════════════════════════════════════
# SCREEN 1 — INPUT
# ═══════════════════════════════════════════════════════
def render_input():
    st.markdown("""<div class="hero-header">
        <div class="hero-badge">🎯 AI-Powered · v2.0</div>
        <h1 class="hero-title">SkillScan <span class="accent">AI</span></h1>
        <p class="hero-subtitle">Skill decomposition · Scenario assessment · Adjacent learning paths</p>
    </div>""", unsafe_allow_html=True)
    render_step_indicator(1)
    st.markdown("<div class='section-gap'></div>", unsafe_allow_html=True)

    with st.expander("🔑 Gemini API Key", expanded=not st.session_state.get("api_key")):
        key = st.text_input("Key", type="password", placeholder="AIzaSy-...", value=st.session_state.get("api_key",""), label_visibility="collapsed")
        if key:
            st.session_state.api_key = key
            st.success("✓ Key saved")

    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.markdown('<div class="card"><h3>📋 Job Description</h3>', unsafe_allow_html=True)
        jd = st.text_area("JD", height=300, placeholder="Paste the full job posting here...", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="card"><h3>📄 Resume</h3>', unsafe_allow_html=True)
        resume = st.text_area("Resume", height=300, placeholder="Paste the candidate resume here...", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div class='section-gap'></div>", unsafe_allow_html=True)
    _, mid, _ = st.columns([1,2,1])
    with mid:
        if st.button("🔍 Analyse & Decompose Skills", use_container_width=True, type="primary"):
            if not st.session_state.get("api_key"):
                st.error("Please enter your API key!")
            elif not jd.strip() or not resume.strip():
                st.error("Please paste both JD and Resume!")
            else:
                with st.spinner("🧠 Decomposing skills into capability layers..."):
                    decomposed = decompose_skills(jd, resume)
                if not decomposed or not decomposed.get("skills"):
                    st.error("Analysis failed. Check your API key and try again.")
                    return
                st.session_state.update({"jd_text": jd, "resume_text": resume,
                    "decomposed": decomposed, "current_step": 2})
                st.rerun()

# ═══════════════════════════════════════════════════════
# SCREEN 2 — SKILL MAP
# ═══════════════════════════════════════════════════════
def render_skill_map():
    render_step_indicator(2)
    d = st.session_state.decomposed
    st.markdown("<div class='section-gap'></div>", unsafe_allow_html=True)

    match = d.get("overall_match_percent", 0)
    color = color_for_score(match / 10)
    st.markdown(f"""<div class="analysis-header">
        <div class="candidate-info">
            <h2>👤 {d.get('candidate_name','Candidate')}</h2>
            <p class="role-badge">Applying for: <strong>{d.get('role_title','Unknown Role')}</strong></p>
            <p style="color:#9ca3af;margin-top:8px">
                ✅ Strong: {', '.join(d.get('strong_areas',[])[:3]) or 'N/A'} &nbsp;|&nbsp;
                ⚠️ Weak: {', '.join(d.get('weak_areas',[])[:3]) or 'N/A'}
            </p>
        </div>
        <div class="match-circle" style="border-color:{color}">
            <span class="match-number" style="color:{color}">{match}%</span>
            <span class="match-label">Match</span>
        </div>
    </div>""", unsafe_allow_html=True)

    st.markdown("### 🧩 Skill Decomposition — Capability Layers")
    layer_names = {"syntax": "🔤 Syntax", "applied": "⚙️ Applied", "problem_solving": "🧩 Problem Solving", "real_world": "🌍 Real-world"}

    for skill in d.get("skills", []):
        priority = skill.get("priority", "Medium")
        p_color = badge_for_priority(priority)
        layers = skill.get("layers", {})

        with st.expander(f"**{skill['name']}** — {skill.get('gap_summary','')}", expanded=True):
            st.markdown(f"""<div style="display:flex;gap:8px;margin-bottom:12px;flex-wrap:wrap">
                <span style="background:{p_color}20;color:{p_color};padding:3px 10px;border-radius:20px;font-size:12px;font-weight:600">{priority} Priority</span>
                <span style="background:#1e2332;color:#9ca3af;padding:3px 10px;border-radius:20px;font-size:12px">Has: {skill.get('claimed_level','?')}</span>
                <span style="background:#1e2332;color:#a78bfa;padding:3px 10px;border-radius:20px;font-size:12px">Needs: {skill.get('required_level','?')}</span>
            </div>""", unsafe_allow_html=True)

            cols = st.columns(4)
            for col, (key, label) in zip(cols, layer_names.items()):
                layer = layers.get(key, {})
                jd_needs = layer.get("jd_needs", False)
                has_it = layer.get("candidate_has", False)
                if not jd_needs:
                    icon, lc, status = "○", "#4b5563", "Not required"
                elif has_it:
                    icon, lc, status = "✓", "#22c55e", "Has it"
                else:
                    icon, lc, status = "✗", "#ef4444", "Gap"
                col.markdown(f"""<div style="background:#111827;border:1px solid #1e2332;border-radius:10px;padding:10px;text-align:center">
                    <div style="font-size:18px;color:{lc}">{icon}</div>
                    <div style="font-size:11px;font-weight:600;color:#e2e8f0;margin:4px 0">{label}</div>
                    <div style="font-size:10px;color:#6b7280">{layer.get('description','')}</div>
                    <div style="font-size:10px;color:{lc};margin-top:4px">{status}</div>
                </div>""", unsafe_allow_html=True)

    st.markdown("<div class='section-gap'></div>", unsafe_allow_html=True)
    st.markdown("### 🎯 Select Skills to Assess")
    all_skills = [s["name"] for s in d.get("skills", [])]
    high_priority = [s["name"] for s in d.get("skills", []) if s.get("priority") == "High"]
    selected = st.multiselect("Skills", options=all_skills, default=high_priority[:3], max_selections=5, label_visibility="collapsed")

    _, mid, _ = st.columns([1,2,1])
    with mid:
        if st.button("🎤 Start Conversational Assessment", use_container_width=True, type="primary"):
            if not selected:
                st.error("Select at least one skill!")
            else:
                st.session_state.update({"skills_to_assess": selected, "current_skill_idx": 0,
                    "current_q_num": 1, "conversation": [], "all_scores": {}, "current_step": 3})
                st.rerun()

# ═══════════════════════════════════════════════════════
# SCREEN 3 — ASSESSMENT
# ═══════════════════════════════════════════════════════
def render_assessment():
    render_step_indicator(3)
    skills = st.session_state.skills_to_assess
    idx = st.session_state.current_skill_idx
    q_num = st.session_state.current_q_num

    if idx >= len(skills):
        with st.spinner("🧠 Mapping adjacent skills and building your plan..."):
            adjacent = map_adjacent_skills(st.session_state.all_scores, st.session_state.decomposed)
            plan = generate_learning_plan(st.session_state.all_scores, adjacent, st.session_state.decomposed)
        st.session_state.update({"adjacent_maps": adjacent, "learning_plan": plan, "current_step": 4})
        st.rerun()
        return

    current_skill = skills[idx]
    skill_data = next((s for s in st.session_state.decomposed.get("skills", []) if s["name"] == current_skill), {})
    layers = skill_data.get("layers", {})
    focus_layer = "applied"
    for lk in ["syntax", "applied", "problem_solving", "real_world"]:
        l = layers.get(lk, {})
        if l.get("jd_needs") and not l.get("candidate_has"):
            focus_layer = lk
            break

    st.markdown("<div class='section-gap'></div>", unsafe_allow_html=True)
    st.progress(idx / len(skills))
    st.markdown(f"""<div class="assessment-header">
        <div class="assessment-progress">
            <span>Skill {idx+1} of {len(skills)}</span>
            <strong>{current_skill}</strong>
            <span style="color:#6b7280;font-size:12px">Focus: {focus_layer.replace('_',' ').title()} layer · Question {q_num} of 3</span>
        </div>
    </div>""", unsafe_allow_html=True)

    conv = st.session_state.conversation
    needs_q = not conv or (conv and conv[-1]["role"] == "candidate" and q_num <= 3)
    if needs_q and q_num <= 3:
        with st.spinner("🤖 Preparing scenario..."):
            question = generate_scenario_question(current_skill, focus_layer, q_num, conv)
        conv.append({"role": "ai", "content": question})
        st.session_state.conversation = conv

    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for msg in conv:
        if msg["role"] == "ai":
            st.markdown(f'<div class="chat-bubble ai-bubble"><div class="bubble-icon">🤖</div><div class="bubble-content">{msg["content"]}</div></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-bubble user-bubble"><div class="bubble-content">{msg["content"]}</div><div class="bubble-icon">👤</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if q_num <= 3:
        with st.form(key=f"form_{idx}_{q_num}"):
            answer = st.text_area("Answer", placeholder="Think out loud — explain your reasoning, not just the answer...", height=120, label_visibility="collapsed")
            submitted = st.form_submit_button("Send →", use_container_width=True)
            if submitted and answer.strip():
                conv.append({"role": "candidate", "content": answer})
                st.session_state.conversation = conv
                st.session_state.current_q_num = q_num + 1
                if q_num + 1 > 3:
                    with st.spinner(f"📊 Scoring {current_skill} with evidence..."):
                        score_data = score_with_evidence(current_skill, layers, conv)
                    st.session_state.all_scores[current_skill] = score_data
                    s = score_data.get("score",5)
                    c = score_data.get("confidence_percent",0)
                    summary = f"✅ Done — **{current_skill}**: {s}/10 | Confidence: {c}%\n\n{score_data.get('verdict','')}"
                    conv.append({"role": "ai", "content": summary})
                    st.session_state.update({"current_skill_idx": idx+1, "current_q_num": 1, "conversation": []})
                st.rerun()

# ═══════════════════════════════════════════════════════
# SCREEN 4 — DASHBOARD (Improvement 7)
# ═══════════════════════════════════════════════════════
def render_dashboard():
    render_step_indicator(4)
    scores = st.session_state.all_scores
    plan = st.session_state.learning_plan
    adjacent = st.session_state.adjacent_maps
    d = st.session_state.decomposed
    st.markdown("<div class='section-gap'></div>", unsafe_allow_html=True)

    # ── SUMMARY
    st.markdown("## 🧾 Summary")
    c1,c2,c3,c4 = st.columns(4)
    for col, label, value in [(c1,"Job Ready",plan.get("overall_readiness","N/A")),
        (c2,"Time Needed",plan.get("time_to_job_ready","N/A")),
        (c3,"Skills Assessed",str(len(scores))),
        (c4,"Match Score",f"{d.get('overall_match_percent',0)}%")]:
        col.markdown(f'<div class="score-card"><div class="score-number" style="color:#a78bfa">{value}</div><div class="score-skill-name">{label}</div></div>', unsafe_allow_html=True)

    col1,col2 = st.columns(2)
    with col1:
        st.markdown(f"""<div class="skill-card matched"><h3>💪 Strong Areas</h3>{''.join([f'<span class="skill-tag matched-tag">{s}</span>' for s in d.get('strong_areas',[])])}</div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="skill-card missing"><h3>🎯 Focus Areas</h3>{''.join([f'<span class="skill-tag missing-tag">{s}</span>' for s in d.get('weak_areas',[])])}</div>""", unsafe_allow_html=True)

    st.markdown("<div class='section-gap'></div>", unsafe_allow_html=True)

    # ── SKILL BREAKDOWN TABLE
    st.markdown("## 🧠 Skill Breakdown")
    st.markdown("""<div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr 1.5fr;gap:8px;padding:8px 16px;background:#1e2332;border-radius:8px;font-size:12px;font-weight:600;color:#6b7280;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:6px">
        <div>Skill</div><div>Your Level</div><div>Required</div><div>Confidence</div><div>Key Gap</div>
    </div>""", unsafe_allow_html=True)

    for skill_name, score_data in scores.items():
        skill_info = next((s for s in d.get("skills",[]) if s["name"]==skill_name), {})
        score = score_data.get("score",5)
        sc = color_for_score(score)
        conf = score_data.get("confidence_percent",0)
        gaps = score_data.get("evidence",{}).get("gaps",[])
        st.markdown(f"""<div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr 1.5fr;gap:8px;padding:12px 16px;background:#111827;border:1px solid #1e2332;border-radius:8px;margin-bottom:6px;font-size:13px;align-items:center">
            <div style="font-weight:600;color:#e2e8f0">{skill_name}</div>
            <div><span style="color:{sc};font-weight:600">{score}/10</span> <span style="color:#6b7280;font-size:11px">{score_data.get('level','')}</span></div>
            <div style="color:#a78bfa;font-size:12px">{skill_info.get('required_level','?')}</div>
            <div><span style="background:{sc}20;color:{sc};padding:2px 8px;border-radius:20px;font-size:11px">{conf}%</span></div>
            <div style="color:#6b7280;font-size:12px">{gaps[0] if gaps else 'See details below'}</div>
        </div>""", unsafe_allow_html=True)

        with st.expander(f"📋 Full evidence — {skill_name}"):
            ev = score_data.get("evidence",{})
            ca, cb = st.columns(2)
            with ca:
                st.markdown("**✅ Strengths:**")
                for s in ev.get("strengths",[]): st.markdown(f"- {s}")
            with cb:
                st.markdown("**⚠️ Gaps:**")
                for g in ev.get("gaps",[]): st.markdown(f"- {g}")
            st.markdown(f"*{ev.get('reasoning','')}*")
            layer_scores = score_data.get("layer_scores",{})
            if layer_scores:
                st.markdown("**Layer scores:**")
                lc = st.columns(4)
                for col,(lname,ls) in zip(lc, layer_scores.items()):
                    c = color_for_score(ls)
                    col.markdown(f'<div style="text-align:center;background:#0d1117;border-radius:8px;padding:8px"><div style="color:{c};font-weight:700">{ls}/10</div><div style="font-size:10px;color:#6b7280">{lname.replace("_"," ").title()}</div></div>', unsafe_allow_html=True)

    st.markdown("<div class='section-gap'></div>", unsafe_allow_html=True)

    # ── ADJACENT PATHS
    st.markdown("## 🧩 Your Realistic Upgrade Path")
    st.markdown("*Not 'learn everything' — just the next step from where you are now*")
    for gap in adjacent.get("gap_maps",[]):
        st.markdown(f'<div class="card" style="border-left:3px solid #6366f1"><h3>🎯 {gap.get("target_skill","")}</h3><p style="color:#9ca3af;font-size:13px">You know: <strong style="color:#e2e8f0">{gap.get("candidate_knows","")}</strong> → JD needs: <strong style="color:#a78bfa">{gap.get("jd_needs","")}</strong></p></div>', unsafe_allow_html=True)
        for i,step in enumerate(gap.get("adjacent_path",[])):
            st.markdown(f'<div style="display:flex;align-items:flex-start;gap:12px;padding:8px 0;border-bottom:1px solid #1e2332"><div style="width:24px;height:24px;background:#6366f1;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;color:white;flex-shrink:0">{i+1}</div><div style="color:#e2e8f0;font-size:13px">{step}</div></div>', unsafe_allow_html=True)
        if gap.get("avoid_jumping_to"):
            st.markdown(f'<div style="background:#450a0a;border-radius:8px;padding:8px 12px;margin-top:8px;font-size:12px;color:#f87171">⛔ Don\'t jump to: {gap["avoid_jumping_to"]}</div>', unsafe_allow_html=True)

    st.markdown("<div class='section-gap'></div>", unsafe_allow_html=True)

    # ── WEEKLY SCHEDULE
    st.markdown("## 🚀 Action Plan")
    weekly = plan.get("weekly_schedule",[])
    if weekly:
        wcols = st.columns(min(len(weekly),3))
        for i,week in enumerate(weekly):
            wcols[i%3].markdown(f'<div class="score-card"><div style="font-size:11px;color:#6366f1;font-weight:600;text-transform:uppercase">{week.get("week_range","")}</div><div style="color:#e2e8f0;font-weight:600;margin:6px 0;font-size:14px">{week.get("focus","")}</div><div style="color:#6b7280;font-size:12px">⏱️ {week.get("daily_hours",2)} hrs/day</div></div>', unsafe_allow_html=True)

    st.markdown("<div class='section-gap'></div>", unsafe_allow_html=True)

    # ── SKILL PLANS
    st.markdown("## 📚 Detailed Learning Plans")
    for sp in plan.get("skill_plans",[]):
        diff = sp.get("difficulty","Medium")
        with st.expander(f"📖 {sp.get('skill','')} — {sp.get('weeks',2)} weeks | {diff}"):
            st.markdown(f'<div style="background:#111827;border-radius:10px;padding:12px 16px;margin-bottom:12px"><div style="color:#9ca3af;font-size:13px">🎯 <strong style="color:#e2e8f0">Why:</strong> {sp.get("why_needed","")}</div><div style="color:#9ca3af;font-size:13px;margin-top:6px">📈 <strong style="color:#e2e8f0">Path:</strong> {sp.get("current_level","")} → {sp.get("target_level","")}</div><div style="color:#9ca3af;font-size:13px;margin-top:6px">⏱️ <strong style="color:#e2e8f0">{sp.get("daily_hours",2)} hrs/day</strong> for {sp.get("weeks",2)} weeks</div></div>', unsafe_allow_html=True)
            st.markdown("**📚 Resources:**")
            type_colors = {"Beginner":"#22c55e","Hands-on":"#6366f1","Project":"#f59e0b"}
            for res in sp.get("resources",[]):
                tc = type_colors.get(res.get("type",""),"#6b7280")
                icon = "🟢" if res.get("type")=="Beginner" else "🔵" if res.get("type")=="Hands-on" else "🟡"
                st.markdown(f'{icon} [{res.get("title","")}]({res.get("url","#")}) <span style="background:{tc}20;color:{tc};padding:1px 8px;border-radius:20px;font-size:11px">{res.get("type","")}</span> — ⏱️ {res.get("duration","")}', unsafe_allow_html=True)
            if sp.get("mini_task"):
                st.markdown(f'<div style="background:#1a1f35;border:1px solid #312e81;border-radius:10px;padding:12px 16px;margin-top:12px"><div style="color:#a5b4fc;font-size:12px;font-weight:600;margin-bottom:4px">🛠️ MINI PROJECT</div><div style="color:#e2e8f0;font-size:13px">{sp["mini_task"]}</div></div>', unsafe_allow_html=True)

    st.markdown(f'<div class="motivation-box">💪 {plan.get("motivational_note","Keep going!")}</div>', unsafe_allow_html=True)
    st.markdown("<div class='section-gap'></div>", unsafe_allow_html=True)
    _,mid,_ = st.columns([1,2,1])
    with mid:
        if st.button("🔄 Assess Another Candidate", use_container_width=True):
            for k in ["jd_text","resume_text","decomposed","skills_to_assess","current_skill_idx","current_q_num","conversation","all_scores","adjacent_maps","learning_plan"]:
                st.session_state.pop(k,None)
            st.session_state.current_step = 1
            st.rerun()

# ═══════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════
def main():
    if "current_step" not in st.session_state:
        st.session_state.current_step = 1
    step = st.session_state.current_step
    if step == 1: render_input()
    elif step == 2: render_skill_map()
    elif step == 3: render_assessment()
    elif step == 4: render_dashboard()

if __name__ == "__main__":
    main()
