

# 🚀 MANTIS

## AI-Powered Developer Learning & GitHub Intelligence Platform

### Built with **ERNIE 4.5 via Novita AI**

---

## 🏆 Hackathon Submission

**Track:** Best ERNIE Multimodal / Reasoning Application
**Inference Provider:** **Novita AI**
**Core Models Used:** **ERNIE 4.5 Series (Baidu)**

---

## 📌 Overview

**MANTIS** is an AI-powered platform that helps developers:

* 📊 Analyze real GitHub repositories
* 🧠 Receive structured code quality feedback
* 🗺️ Generate job-ready learning roadmaps
* 🧪 Evaluate submitted code with AI mentoring
* 📈 Track learning and skill progression over time

Unlike generic AI tools, **MANTIS deeply inspects actual repositories** (files, README, code samples) and converts them into **measurable learning intelligence**.

---

## ✨ Core Novelty

### 🔹 1. Repository-Level AI Intelligence (Not Prompt-Only)

* Downloads **entire GitHub repo as ZIP**
* Extracts:

  * File types & structure
  * README quality
  * Representative code samples
* Sends **structured repository context** to ERNIE
* Produces **numerical scores + actionable insights**

👉 This avoids hallucinations and ensures **evidence-based evaluation**

---

### 🔹 2. Multi-Model ERNIE Usage (Feature-Specific)

| Feature                     | ERNIE Model Used                   | Why                                                  |
| --------------------------- | ---------------------------------- | ---------------------------------------------------- |
| GitHub repository analysis  | `baidu/ernie-4.5-vl-424b-a47b`     | Large-context + multimodal reasoning over many files |
| Learning roadmap generation | `baidu/ernie-4.5-21B-a3b-thinking` | Strong instruction following + curriculum reasoning  |
| Code evaluation & feedback  | `baidu/ernie-4.5-21B-a3b-thinking` | Step-by-step reasoning + scoring consistency         |

👉 **Each model is chosen intentionally**, not randomly.

---

## 🧠 Features

---

### 1️⃣ GitHub Repository Analyzer (AI Code Review)

**What it does:**

* Accepts any public GitHub repo
* Downloads & parses repository ZIP
* Evaluates:

  * Documentation quality
  * Code quality
  * Maintainability
  * Estimated developer level

**AI Output (strict JSON):**

```json
{
  "documentation_score": 82,
  "code_quality_score": 76,
  "maintainability_score": 79,
  "estimated_developer_level": "intermediate",
  "strengths": [],
  "weaknesses": [],
  "improvement_suggestions": []
}
```

📌 **Model used:**
`baidu/ernie-4.5-vl-424b-a47b`

---

### 2️⃣ Learning Roadmap Generator (Job-Ready Curriculum)

**Input:** Any skill (e.g. *Python*, *Computer Vision*, *Web Development*)

**Output:**

* EXACTLY **10 progressive roadmap items**
* Beginner → Advanced
* Each item includes:

  * Skills
  * Prerequisites
  * Hands-on projects
* Stored in DB & reusable

📌 **Model used:**
`baidu/ernie-4.5-21B-a3b-thinking`

---

### 3️⃣ AI Code Evaluation & Mentoring

Users submit:

* Task description
* Source code

AI returns:

* Feedback list
* Improved code
* Numerical score (0–100)

Uses **strict JSON contracts** for reliability.

📌 **Model used:**
`baidu/ernie-4.5-21B-a3b-thinking`

---

### 4️⃣ Learning Progress Tracking

* Stores **historical repo analysis**
* Generates:

  * Progress graphs
  * Growth summaries
  * Language-wise skill estimates

This turns GitHub activity into **learning analytics**.

---

### 5️⃣ AI-Generated Developer Profile & Resume Signals

Based on repository history:

* Average scores
* Strongest languages
* Overall growth trend
* Skill maturity summary

📌 Designed for **students, self-learners & early-career developers**

---

## 🏗️ Technical Architecture

### Backend

* Python
* Flask
* SQLite
* Flask-CORS

### AI Layer

* ERNIE 4.5 models via **Novita AI**
* OpenAI-compatible API
* Strict JSON-only prompting
* Regex-based safe extraction

### Data Flow

```
GitHub Repo → ZIP Download
           → File & Code Parsing
           → ERNIE Analysis
           → Structured Scores
           → Learning Feedback Loop
```

---

## 📂 Project Structure

```
ERINE_NOVITA/
│
├── app.py                     # Main Flask application
├── users.db                   # SQLite database
├── requirements.txt
├── runtime.txt
│
├── services/
│   ├── github_service.py      # GitHub API utilities
│   └── github_analyzer.py     # ERNIE-powered repo analysis
│
├── templates/
│   ├── index.html
│   ├── github.html
│   ├── learning.html
│   ├── profile.html
│   └── resume.html
│
├── static/
│   └── data/
│
└── README.md
```

---

## ⚙️ Local Setup

### 1️⃣ Clone

```bash
git clone https://github.com/oneVisionary/ERINE_NOVITA.git
cd ERINE_NOVITA
```

### 2️⃣ Environment

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3️⃣ Configure `.env`

```env
NOVITA_API_KEY=your_novita_api_key
FLASK_SECRET_KEY=your_secret_key
```

### 4️⃣ Run

```bash
python app.py
```

---

## 🎯 Why This Project Stands Out

✔ Uses **real repositories**, not toy examples
✔ ERNIE used as a **reasoning engine**, not a chatbot
✔ Strong **JSON contracts** & reliability handling
✔ Clear **learning feedback loop**
✔ Production-ready Flask architecture

---

## 🔮 Future Enhancements

* Auto PR review assistant
* Team dashboards for classrooms
* Multi-agent curriculum planning
* Resume PDF export
* Cloud deployment & CI integration

---

## 🙏 Acknowledgements

* **Baidu ERNIE Team**
* **Novita AI**
* Open-source community

---

## 📜 License

Educational & hackathon use.
Free to extend and modify.

Just tell me 💪
