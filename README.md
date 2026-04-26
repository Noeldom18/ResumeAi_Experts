# 🎯 SkillScan AI — AI-Powered Skill Assessment & Personalised Learning Plan Agent

> *A resume tells you what someone claims to know — not how well they actually know it.*
> **SkillScan AI** fixes that with deep skill decomposition, scenario-based assessment, and personalised learning paths.

---

## 🌟 What It Does

Most hiring tools just match keywords. SkillScan AI goes deeper.

It takes a **Job Description** and a **candidate's resume**, then:

1. **Decomposes** every skill into 4 capability layers — Syntax, Applied, Problem Solving, Real-world
2. **Maps gaps** precisely — not just "missing Python" but "knows Python syntax, lacks API integration and debugging"
3. **Assesses conversationally** — scenario-based questions, not MCQs or definitions
4. **Scores with evidence** — confidence percentage + specific strengths and gaps found
5. **Generates adjacent learning paths** — realistic next steps from where the candidate actually is
6. **Creates a personalised plan** — real free resources, time estimates based on current level, mini projects

---



## 🌐 Live App
👉 [Try it Live](https://resumeaiexperts-7yexrxccagcgo5l9iz2xuf.streamlit.app/)

---

## 🖼️ Screenshots

### Step 1 — Input Screen
Paste any Job Description and Resume

### Step 2 — Skill Decomposition Map
Every skill broken into 4 layers — see exactly where the gap is

### Step 3 — Conversational Assessment
Scenario-based questions that test real practical thinking

### Step 4 — Results Dashboard
Scores, evidence, adjacent paths, weekly action plan

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        SKILLSCAN AI                             │
│                                                                 │
│   ┌──────────┐   ┌──────────────┐   ┌────────────┐   ┌──────┐  │
│   │  INPUT   │──▶│  SKILL MAP   │──▶│ ASSESSMENT │──▶│ DASH │  │
│   │          │   │              │   │            │   │BOARD │  │
│   │ JD +     │   │ Decompose    │   │ 3 scenario │   │      │  │
│   │ Resume   │   │ into layers  │   │ questions  │   │Scores│  │
│   └──────────┘   └──────────────┘   │ per skill  │   │ Plan │  │
│                                     └────────────┘   └──────┘  │
│                                                                 │
│   ─────────────────── Google Gemini API ─────────────────────   │
│                                                                 │
│   Call 1          Call 2           Call 3          Call 4       │
│   Skill           Gap              Scenario        Learning     │
│   Extractor       Analyser         Interviewer     Planner      │
└─────────────────────────────────────────────────────────────────┘
```

### How It Works — Step by Step

```
User pastes JD + Resume
        ↓
AI Call 1 — Gemini extracts and decomposes all skills into 4 layers
        ↓
AI Call 2 — Compares resume against each layer (matched / partial / gap)
        ↓
User selects skills to be assessed
        ↓
AI Call 3a — Generates scenario question 1 (conceptual)
AI Call 3b — Follow-up question 2 based on answer (practical)
AI Call 3c — Question 3 (scale / failure / optimisation challenge)
        ↓
AI Call 3d — Scores skill with confidence % and specific evidence
        ↓
AI Call 4 — Maps adjacent upgrade paths (not generic "learn X")
        ↓
AI Call 5 — Generates personalised plan with real resources + timeline
        ↓
Dashboard shows: Summary · Skill table · Adjacent paths · Weekly plan
```

---

## 🔑 7 Core Innovations

### 1. Skill Decomposition into Capability Layers
Every skill is broken into 4 layers:
- **Syntax** — basic knowledge (loops, functions, data types)
- **Applied** — practical use (file handling, APIs, libraries)
- **Problem Solving** — algorithmic thinking (DSA, logic)
- **Real-world** — production experience (debugging, optimisation, scaling)

Output: *"You know Python at syntax level, but the role needs API integration and debugging"*

### 2. Conversational Scenario Assessment
Instead of asking *"What is a list?"*, the AI asks:
*"Suppose you need to process 1 million records from a file. How would you design it?"*

Questions adapt dynamically based on the previous answer — just like a real technical interview.

### 3. Confidence + Evidence Scoring
Not just a number. Every score includes:
- Confidence percentage (how sure the model is)
- Specific strengths observed
- Specific gaps found
- Layer-by-layer breakdown

Output: *"Python: Intermediate (72% confidence) — Gap: lacks real-world debugging and scaling experience"*

### 4. Adjacent Skill Gap Mapping
Instead of *"Learn Machine Learning"*, the system says:
- Start with Pandas + data cleaning (you already know Python)
- Then Scikit-learn basics (builds on your stats knowledge)
- Then model evaluation
- Avoid jumping to Deep Learning (too far from current level)

### 5. Realistic Time Estimates
Time is calculated based on actual current level:
- Beginner → Intermediate = 4–6 weeks
- Intermediate → Proficient = 2–3 weeks

### 6. Practical Learning Plans
Each skill plan includes:
- 1 Beginner resource
- 1 Hands-on resource
- 1 Project with a specific mini-task

### 7. Full Results Dashboard
- Summary card with match %, readiness, time needed
- Skill breakdown table with confidence scores
- Adjacent upgrade paths with step-by-step progression
- Weekly action schedule
- Detailed plans with clickable resources

---

## 🛠️ Tech Stack

| Part | Technology | Why |
|------|-----------|-----|
| Frontend | Streamlit (Python) | Fast to build, easy to deploy, no HTML/CSS/JS needed |
| AI Engine | Google Gemini 2.0 Flash | Free tier, high quality, fast responses |
| Language | Python 3.9+ | Simple and widely supported |
| Hosting | Streamlit Cloud | Free, one-click deploy from GitHub |
| Styling | Custom CSS | Dark professional theme |

**APIs Used:**
- Google Gemini API — completely free via Google AI Studio
- No other paid APIs or services

---

## 🚀 Local Setup — Run in 5 Minutes

### Prerequisites
- Python 3.9 or higher
- A free Google Gemini API key from **aistudio.google.com**

### Steps

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/skillscan-ai.git
cd skillscan-ai

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
streamlit run app.py
```

App opens at **http://localhost:8501**

### Get Your Free API Key
1. Go to **aistudio.google.com**
2. Sign in with Google
3. Click **"Get API Key"** → **"Create API Key"**
4. Copy and paste it into the app when it asks

---

## ☁️ Deploy on Streamlit Cloud (Free)

1. Push this repo to GitHub
2. Go to **share.streamlit.io**
3. Click **New App** → connect your GitHub
4. Set `app.py` as the main file
5. Click **Deploy**

Done in under 3 minutes. You get a free public URL.

---

## 📁 Project Structure

```
skillscan-ai/
├── app.py                  # Complete Streamlit application (all logic + UI)
├── requirements.txt        # Python dependencies
├── assets/
│   └── style.css           # Custom dark theme
└── README.md               # This file
```

---

## 📦 Requirements

```
streamlit==1.40.0
google-generativeai
```

---

## 📊 Sample Input & Output

### Sample Job Description
```
Senior Data Analyst — FinTech Startup

Requirements:
- 3+ years SQL (complex queries, window functions, CTEs)
- Python for data analysis (pandas, numpy)
- Data visualisation — Tableau or Power BI
- Statistical analysis and A/B testing
- Strong communication and storytelling with data
- Excel advanced (pivot tables, VLOOKUP, macros)
```

### Sample Resume
```
Jane Doe | jane@email.com

Experience:
Junior Data Analyst, ABC Corp (2022–Present)
- SQL queries for weekly reporting
- Excel dashboards for marketing team

Skills: Excel, SQL (basic), Python (beginner), communication
Education: B.Sc Mathematics 2021
```

### Sample Output

**Skill Decomposition:**
| Skill | Syntax | Applied | Problem Solving | Real-world |
|-------|--------|---------|-----------------|------------|
| SQL | ✓ Has | ✗ Gap | ○ Not required | ✗ Gap |
| Python | ✓ Has | ✗ Gap | ✗ Gap | ✗ Gap |
| Tableau | ✗ Gap | ✗ Gap | ○ Not required | ✗ Gap |

**Assessment Scores:**
| Skill | Score | Level | Confidence |
|-------|-------|-------|------------|
| SQL | 5/10 | Intermediate | 68% |
| Python | 3/10 | Beginner | 74% |
| Tableau | 2/10 | Beginner | 81% |

**Learning Plan:**
- Overall readiness: **42%**
- Time to job ready: **3 months**
- Week 1–2: SQL depth (window functions, CTEs)
- Week 3–4: Python pandas + numpy
- Week 5–6: Tableau basics + build 2 dashboards
- Week 7: Mini project — end-to-end analysis

---

## 🧠 Scoring Logic

| Score | Level | Meaning |
|-------|-------|---------|
| 1–3 | Beginner | Basic awareness only |
| 4–6 | Intermediate | Can do with guidance |
| 7–8 | Proficient | Can do independently |
| 9–10 | Expert | Can teach others |

Confidence % = how certain the AI is about the score based on answer quality and depth.

Skills scoring below 7 are included in the learning plan.

---

## 👤 Built By

**[Noel Dominic]**
- GitHub: https://github.com/Noeldom18
- Email: noeldom1999@gmail.com

---

## 📄 License

MIT License — free to use and modify.

---

*Built for the Deccan AI Hackathon 2026*
