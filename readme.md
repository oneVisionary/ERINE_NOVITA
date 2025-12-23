

# 🐜 MANTIS – AI-Powered Developer Learning & GitHub Intelligence Platform  
### Powered by ERNIE 4.5 (Novita AI)

An **AI-driven learning and developer growth platform** that combines **personalized learning roadmaps**, **GitHub repository analysis**, and **AI-generated developer profiling** using **ERNIE 4.5 (via Novita AI)**.

This platform helps developers:

* Learn **any skill step-by-step**
* Build **real-world, portfolio-ready projects**
* Track learning progress
* Analyze GitHub code quality
* Generate AI-powered developer profiles and resumes

---

## 🧠 AI Models Used & Their Impact

### 🔹 ERNIE 4.5 (Baidu) via Novita AI

**Model:** `baidu/ernie-4.5-21B-a3b-thinking`

ERNIE is the **core intelligence** behind the platform.

### How ERNIE impacts this application:

#### 1️⃣ AI Learning Roadmap Generator

* Converts **any user-entered skill** (e.g., Computer Vision, Web Development, ML, DevOps) into:

  * 6 structured stages
  * Grouped as **Basic / Intermediate / Advanced**
  * Each stage contains **5 real-world projects**
* Ensures projects are:

  * Practical
  * Recruiter-friendly
  * GitHub-submittable
* Adds:

  * Skills learned per project
  * Technical requirements
  * High-quality reference links


---

#### 2️⃣ AI Code Evaluation Engine

* Reviews submitted code
* Generates:

  * Score (0–100)
  * Actionable feedback
  * Improved version of the code
* Ensures beginner-friendly, instructor-level evaluation

📌 *Acts like a personal coding mentor.*

---

#### 3️⃣ GitHub Repository Analyzer

* Fetches public repositories
* Uses AI to analyze:

  * Documentation quality
  * Code quality
  * Maintainability
* Tracks historical progress over time
* Visualizes learning improvement using charts

📌 *Turns GitHub into a learning analytics dashboard.*

---

#### 4️⃣ AI Developer Profile & Resume Generator

* Summarizes developer growth
* Identifies strengths, weaknesses, and improvement trends
* Generates:

  * Professional profile summaries
  * Resume-ready metrics
  * Shareable developer reports

📌 *Transforms raw GitHub data into career insights.*

---

## ✨ Key Features

### 🎓 Learning Zone

* AI-generated learning roadmaps
* Skill-based curriculum (any domain)
* Project-based progression
* GitHub submission validation
* Locked/unlocked stages based on completion

### 🧑‍💻 GitHub Intelligence

* GitHub account integration
* Repository syncing
* AI-powered code analysis
* Learning progress graphs
* Improvement suggestions

### 📊 Dashboard

* Total users
* Repositories analyzed
* Average code quality
* Learning analytics

### 🪪 Developer Profile

* AI-generated performance summary
* Primary language detection
* Growth trend analysis
* Shareable profile & resume export

---

## 🛠 Tech Stack

**Backend**

* Python
* Flask
* SQLite
* OpenAI-compatible SDK (Novita AI)

**Frontend**

* HTML (Jinja templates)
* Bootstrap
* JavaScript
* Chart.js
* ACE Editor

**AI**

* ERNIE 4.5 (via Novita AI)

---

## 📂 Project Structure

```
ERINE_NOVITA/
│
├── app.py
├── users.db
├── .env
├── services/
│   ├── github_service.py
│   └── github_analyzer.py
│
├── templates/
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── github.html
│   ├── learning.html
│   ├── profile.html
│   └── resume.html
│
├── static/
│   ├── assets/
│
└── README.md
```

---

## ⚙️ Local Setup & Installation

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/ERINE_NOVITA.git
cd ERINE_NOVITA
```

---

### 2️⃣ Create Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows
```

---

### 3️⃣ Install Dependencies

```bash
pip install flask python-dotenv werkzeug openai
```

---

### 4️⃣ Setup Environment Variables

Create a `.env` file in the root directory:

```env
NOVITA_API_KEY=your_novita_api_key_here
```

⚠️ **Important:**
You must have access to **Novita AI** and the **ERNIE model**.

---

### 5️⃣ Run the Application

```bash
python app.py
```

The app will start at:

```
http://127.0.0.1:5000
```

---

## 🚀 How to Use

1. **Sign up / Log in**
2. **Connect GitHub account**
3. Navigate to **Learning Zone**
4. Enter any skill (e.g., `computer vision`)
5. Generate AI learning roadmap
6. Complete projects & submit GitHub links
7. Analyze repositories
8. View AI-generated profile & resume

---

## 🔮 Future Enhancements

* Role-based learning paths (Frontend, Backend, ML Engineer)
* Auto GitHub PR reviews
* Certification generation
* AI interview preparation
* Team & classroom mode
* Cloud deployment (Docker + AWS)

---

## ❤️ Acknowledgements

* **Baidu ERNIE AI**
* **Novita AI Platform**
* Open-source community
* Hackathon inspiration

---

## 📜 License

This project is for **educational and hackathon use**.
You are free to modify and extend it.

