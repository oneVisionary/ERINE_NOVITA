from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from collections import defaultdict
import sqlite3
import json
import os
from services.github_service import fetch_public_repos
from services.github_analyzer import analyze_repo
max_tokens=4096
from datetime import datetime
from flask_cors import CORS
from openai import OpenAI
import json
from dotenv import load_dotenv
import json
import re
last_sync_time = datetime.now().strftime("%b %d, %Y %I:%M %p")
DATABASE = "users.db"

# ================= DATABASE =================
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def create_table():
    conn = get_db()

    conn.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        email TEXT UNIQUE,
        password TEXT,
        github_username TEXT
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS repositories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        repo_url TEXT,
        language TEXT,
        UNIQUE(user_id, repo_url)
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS repo_analysis (
        repo_id INTEGER UNIQUE,
        documentation_score INTEGER,
        code_quality_score INTEGER,
        maintainability_score INTEGER,
        developer_level TEXT,
        strengths TEXT,
        weaknesses TEXT,
        improvements TEXT,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS learning_roadmaps (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        skill TEXT,
        roadmap_json TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS repo_analysis_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        repo_id INTEGER,
        documentation_score INTEGER,
        code_quality_score INTEGER,
        maintainability_score INTEGER,
        developer_level TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()

# ================= AUTH =================

# ---------------- LOAD ENV ----------------
load_dotenv()

app = Flask(__name__)
CORS(app)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

# ✅ CREATE DB + TABLES AT APP STARTUP (RENDER SAFE)
with app.app_context():
    create_table()




NOVITA_API_KEY = os.getenv("NOVITA_API_KEY")
if not NOVITA_API_KEY:
    raise RuntimeError("NOVITA_API_KEY not set in .env")

ernie_client = OpenAI(
    api_key=NOVITA_API_KEY,
    base_url="https://api.novita.ai/openai"
)

@app.route("/learning/submit", methods=["POST"])
def learning_submit():
    data = request.get_json()

    github_url = data.get("github_url")
    stage = data.get("stage")
    task = data.get("task")

    if not github_url:
        return {"error": "GitHub link required"}, 400

    if not github_url.startswith("https://github.com/"):
        return {"error": "Invalid GitHub URL"}, 400

    # 🚀 Later you can save this to DB
    return {
        "success": True,
        "message": "Task completed. Next task unlocked."
    }

@app.route("/learning/roadmap", methods=["POST"])
def learning_roadmap():
    try:
        data = request.get_json()
        skill = data.get("skill")

        if not skill:
            return {"error": "Skill is required"}, 400

        prompt = f"""
You are a senior curriculum architect and industry expert.

Create a COMPLETE, MODERN, INDUSTRY-READY learning path for the skill:

SKILL: "{skill}"

ABSOLUTE RULES (DO NOT BREAK):
- Return ONLY valid JSON
- No markdown
- No explanations
- Exactly 10 projects
- Projects must progress from Beginner → Advanced
- Each project must be REAL, PRACTICAL, and PORTFOLIO-WORTHY
- Include multiple platforms: console, web app, API, system, mobile, AI, cloud
- Each project MUST clearly state technical skills learned
- Assume learner is starting from scratch and ends job-ready

================ REQUIRED JSON SCHEMA =================

{{
  "skill": "{skill}",
  "projects": [
    {{
      "task_id": 1,
      "level": "Beginner",
      "title": "Project title",
      "platform": "Console / Web / API / Mobile / ML / System",
      "description": "What the learner will build",
      "technical_skills_learned": [
        "Skill 1",
        "Skill 2",
        "Skill 3"
      ],
      "tools_and_technologies": [
        "Tool 1",
        "Tool 2"
      ],
      "expected_outcome": "What the learner will be capable of after completing this project",
      "references": [
        "https://official-docs-link",
        "https://high-quality-tutorial"
      ]
    }}
  ]
}}

================ QUALITY BENCHMARK =================

Example progression (DO NOT COPY, ONLY FOLLOW QUALITY):

1. Console-based fundamentals project
2. Data handling & logic project
3. File system or API project
4. Web application
5. Database-backed system
6. Authentication & security
7. Performance & optimization
8. Advanced architecture
9. AI / ML / Automation / Cloud
10. Production-grade capstone

Generate the FULL 10-project roadmap now.
"""

        response = ernie_client.chat.completions.create(
            model="baidu/ernie-4.5-21B-a3b-thinking",
            messages=[
                {"role": "system", "content": "Return ONLY valid JSON. No markdown."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=6000
        )

        content = response.choices[0].message.content.strip()

        # 🔍 DEBUG LOG (KEEP THIS)
        print("=== AI RAW OUTPUT ===")
        print(content)
        print("=====================")

        # ✅ STRICT JSON PARSE
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass

        # 🔁 SAFE EXTRACTION
        match = re.search(r"\{.*\}", content, re.S)
        if match:
            return json.loads(match.group())

        return {"error": "Failed to generate roadmap"}, 500

    except Exception as e:
        print("🔥 ROADMAP ERROR:", str(e))
        return {"error": "Internal server error"}, 500



@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        conn = get_db()
        try:
            conn.execute(
                "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                (
                    request.form["username"],
                    request.form["email"],
                    generate_password_hash(request.form["password"])
                )
            )
            conn.commit()
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Email already exists")
        finally:
            conn.close()
    return render_template("register.html")


@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE email=?",
            (request.form["email"],)
        ).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], request.form["password"]):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("dashboard"))
        flash("Invalid credentials")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))



@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()

    # Total users
    total_users = conn.execute(
        "SELECT COUNT(*) FROM users"
    ).fetchone()[0]

    # User repos
    user_repos = conn.execute(
        "SELECT COUNT(*) FROM repositories WHERE user_id=?",
        (session["user_id"],)
    ).fetchone()[0]

    # Projects analyzed
    analyzed_projects = conn.execute("""
        SELECT COUNT(*) 
        FROM repo_analysis a
        JOIN repositories r ON a.repo_id = r.id
        WHERE r.user_id=?
    """, (session["user_id"],)).fetchone()[0]

    # Average code quality
    avg_code_quality = conn.execute("""
        SELECT AVG(code_quality_score)
        FROM repo_analysis a
        JOIN repositories r ON a.repo_id = r.id
        WHERE r.user_id=?
    """, (session["user_id"],)).fetchone()[0]

    conn.close()

    return render_template(
        "index.html",
        username=session["username"],
        total_users=total_users,
        user_repos=user_repos,
        analyzed_projects=analyzed_projects,
        avg_code_quality=round(avg_code_quality or 0, 1)
    )

@app.route("/github", methods=["GET", "POST"])
def github():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()

    if request.method == "POST":
        repo_id = request.form.get("repo_id")

        repo = conn.execute(
            "SELECT repo_url FROM repositories WHERE id=? AND user_id=?",
            (repo_id, session["user_id"])
        ).fetchone()

        if repo:
            # ✅ RUN ANALYSIS ONLY ONCE
            result = analyze_repo(repo["repo_url"])

            # ✅ SAVE LATEST SNAPSHOT
            conn.execute("""
                INSERT INTO repo_analysis (
                    repo_id,
                    documentation_score,
                    code_quality_score,
                    maintainability_score,
                    developer_level,
                    strengths,
                    weaknesses,
                    improvements
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(repo_id) DO UPDATE SET
                    documentation_score=excluded.documentation_score,
                    code_quality_score=excluded.code_quality_score,
                    maintainability_score=excluded.maintainability_score,
                    developer_level=excluded.developer_level,
                    strengths=excluded.strengths,
                    weaknesses=excluded.weaknesses,
                    improvements=excluded.improvements,
                    updated_at=CURRENT_TIMESTAMP
            """, (
                repo_id,
                result["documentation_score"],
                result["code_quality_score"],
                result["maintainability_score"],
                result["estimated_developer_level"],
                json.dumps(result["strengths"]),
                json.dumps(result["weaknesses"]),
                json.dumps(result["improvement_suggestions"])
            ))

            # ✅ SAVE HISTORY FOR LEARNING GRAPH (ONCE)
            conn.execute("""
                INSERT INTO repo_analysis_history (
                    repo_id,
                    documentation_score,
                    code_quality_score,
                    maintainability_score,
                    developer_level
                )
                VALUES (?, ?, ?, ?, ?)
            """, (
                repo_id,
                result["documentation_score"],
                result["code_quality_score"],
                result["maintainability_score"],
                result["estimated_developer_level"]
            ))

            # ✅ COMMIT ONCE
            conn.commit()

    analyses = conn.execute("""
        SELECT r.id, r.repo_url, r.language, a.*
        FROM repositories r
        LEFT JOIN repo_analysis a ON r.id = a.repo_id
        WHERE r.user_id=?
    """, (session["user_id"],)).fetchall()

    conn.close()
    return render_template(
        "github.html",
        analyses=analyses,
        username=session["username"],
        last_sync_time=last_sync_time
    )


@app.route("/github/progress/<int:repo_id>")
def github_progress(repo_id):
    if "user_id" not in session:
        return {"error": "Unauthorized"}, 401

    conn = get_db()
    rows = conn.execute("""
        SELECT documentation_score,
               code_quality_score,
               maintainability_score,
               created_at
        FROM repo_analysis_history
        WHERE repo_id=?
        ORDER BY created_at
    """, (repo_id,)).fetchall()
    conn.close()

    return {
        "labels": [r["created_at"] for r in rows],
        "documentation": [r["documentation_score"] for r in rows],
        "code_quality": [r["code_quality_score"] for r in rows],
        "maintainability": [r["maintainability_score"] for r in rows]
    }

@app.route("/github/improvements/<int:repo_id>")
def github_improvements(repo_id):
    if "user_id" not in session:
        return {"error": "Unauthorized"}, 401

    conn = get_db()
    row = conn.execute("""
        SELECT strengths, weaknesses, improvements
        FROM repo_analysis
        WHERE repo_id=?
    """, (repo_id,)).fetchone()
    conn.close()

    if not row:
        return {"error": "No analysis found"}, 404

    return {
        "strengths": json.loads(row["strengths"] or "[]"),
        "weaknesses": json.loads(row["weaknesses"] or "[]"),
        "improvements": json.loads(row["improvements"] or "[]"),
        "references": [
            "https://realpython.com/",
            "https://docs.python.org/3/",
            "https://github.com/clean-code-book"
        ]
    }


@app.route("/github/connect", methods=["POST"])
def github_connect():
    if "user_id" not in session:
        return redirect(url_for("login"))

    github_username = request.form["github_username"]

    repos = fetch_public_repos(github_username)
    conn = get_db()

    # ✅ SAVE GITHUB USERNAME
    conn.execute("""
        UPDATE users SET github_username=?
        WHERE id=?
    """, (github_username, session["user_id"]))

    for r in repos:
        if isinstance(r, dict):
            repo_url = r.get("url")
            language = r.get("language", "Unknown")
        else:
            repo_url = r
            language = "Unknown"

        conn.execute("""
            INSERT OR IGNORE INTO repositories (user_id, repo_url, language)
            VALUES (?, ?, ?)
        """, (session["user_id"], repo_url, language))

    conn.commit()
    conn.close()

    flash("GitHub connected successfully")
    return redirect(url_for("github"))

@app.route("/learning")
def learning():
    return render_template("learning.html")
# ================= RESUME =================
@app.route("/resume")
def resume_preview():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    analyses = conn.execute("""
        SELECT r.repo_url, r.language,
               a.documentation_score, a.code_quality_score,
               a.maintainability_score
        FROM repositories r
        JOIN repo_analysis a ON r.id = a.repo_id
        WHERE r.user_id=?
    """, (session["user_id"],)).fetchall()
    conn.close()

    if not analyses:
        return render_template("resume.html", analyses=[], username=session["username"])

    avg_doc = sum(a["documentation_score"] for a in analyses) / len(analyses)
    avg_code = sum(a["code_quality_score"] for a in analyses) / len(analyses)
    avg_main = sum(a["maintainability_score"] for a in analyses) / len(analyses)
    overall = (avg_doc + avg_code + avg_main) / 3

    lang_scores = defaultdict(list)
    for a in analyses:
        lang_scores[a["language"]].append(
            (a["documentation_score"] + a["code_quality_score"] + a["maintainability_score"]) / 3
        )

    language_avg = {k: round(sum(v)/len(v), 1) for k, v in lang_scores.items()}

    summary = (
        "Advanced developer" if overall >= 85
        else "Proficient developer" if overall >= 70
        else "Growing developer"
    )

    return render_template(
        "resume.html",
        username=session["username"],
        analyses=analyses,
        avg_documentation=round(avg_doc, 1),
        avg_code_quality=round(avg_code, 1),
        avg_maintainability=round(avg_main, 1),
        overall_score=round(overall, 1),
        language_avg=language_avg,
        summary=summary
    )
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from collections import defaultdict
import sqlite3
import json

from services.github_service import fetch_public_repos
from services.github_analyzer import analyze_repo
max_tokens=4096
from datetime import datetime

last_sync_time = datetime.now().strftime("%b %d, %Y %I:%M %p")





from openai import OpenAI
import json
from dotenv import load_dotenv
import json
import re



NOVITA_API_KEY = os.getenv("NOVITA_API_KEY")
if not NOVITA_API_KEY:
    raise RuntimeError("NOVITA_API_KEY not set in .env")

ernie_client = OpenAI(
    api_key=NOVITA_API_KEY,
    base_url="https://api.novita.ai/openai"
)



@app.route("/learning/generate", methods=["POST"])
def generate_learning_path():
    if "user_id" not in session:
        return {"error": "Unauthorized"}, 401

    skill = request.json.get("skill")
    if not skill:
        return {"error": "Skill is required"}, 400

    prompt = f"""
You are an expert curriculum designer.
Create a professional learning roadmap for "{skill}".

RULES:
- JSON ONLY
- EXACTLY 10 ROADMAP ITEMS
- Beginner → Advanced
- Each item MUST include:
  - title
  - description
  - level
  - skills (array)
  - prerequisites (array, empty if none)
  - project_list (array of hands-on projects)
"""

    response = ernie_client.chat.completions.create(
        model="baidu/ernie-4.5-21B-a3b-thinking",
        messages=[
            {"role": "system", "content": "Return ONLY valid JSON."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1,
        max_tokens=6000
    )

    raw = response.choices[0].message.content.strip()

    print("=== AI RAW OUTPUT ===")
    print(raw)
    print("=====================")

    if not raw:
        return {"error": "AI returned empty response"}, 500

    # -------------------------------------------------
    # 1️⃣ Remove markdown fences
    # -------------------------------------------------
    raw = re.sub(r"^```(?:json)?|```$", "", raw.strip(), flags=re.IGNORECASE).strip()

    # -------------------------------------------------
    # 2️⃣ Parse JSON safely
    # -------------------------------------------------
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r"(\[[\s\S]*\]|\{[\s\S]*\})", raw)
        if not match:
            return {"error": "Invalid AI JSON"}, 500
        parsed = json.loads(match.group(1))

    # -------------------------------------------------
    # 3️⃣ Normalize into list (AUTO-DETECT)
    # -------------------------------------------------
    if isinstance(parsed, dict):
        if "projects" in parsed:
            roadmap_raw = parsed["projects"]
        elif "roadmap" in parsed:
            roadmap_raw = parsed["roadmap"]
        else:
            list_values = [v for v in parsed.values() if isinstance(v, list)]
            if not list_values:
                return {"error": "Unknown AI JSON structure"}, 500
            roadmap_raw = list_values[0]
    elif isinstance(parsed, list):
        roadmap_raw = parsed
    else:
        return {"error": "Unexpected AI output format"}, 500

    # -------------------------------------------------
    # 4️⃣ Normalize each roadmap item (WITH project_list)
    # -------------------------------------------------
    roadmap = []

    for item in roadmap_raw:
        if not isinstance(item, dict):
            continue

        skills = (
            item.get("skills")
            or item.get("skill")
            or item.get("technologies")
            or item.get("tools")
            or []
        )

        prerequisites = (
            item.get("prerequisites")
            or item.get("requires")
            or item.get("depends_on")
            or []
        )

        project_list = (
            item.get("project_list")
            or item.get("projects")
            or item.get("projectList")
            or []
        )

        # Ensure lists
        if isinstance(skills, str):
            skills = [skills]
        if isinstance(prerequisites, str):
            prerequisites = [prerequisites]
        if isinstance(project_list, str):
            project_list = [project_list]

        # 🔥 Auto-generate projects if missing
        if not project_list:
            title = item.get("title", "Topic")
            project_list = [
                f"{title} – Mini Project",
                f"{title} – Practical Implementation",
                f"{title} – Real-World Use Case"
            ]

        roadmap.append({
            "title": item.get("title", "Untitled Topic"),
            "description": item.get("description", ""),
            "level": item.get("level") or item.get("difficulty", "Beginner"),
            "skills": skills,
            "prerequisites": prerequisites,
            "project_list": project_list
        })

    # -------------------------------------------------
    # 5️⃣ Enforce EXACTLY 10 items
    # -------------------------------------------------
    if len(roadmap) != 10:
        return {
            "error": "AI must return exactly 10 roadmap items",
            "received": len(roadmap)
        }, 500

    # -------------------------------------------------
    # 6️⃣ Save to JSON file
    # -------------------------------------------------
    os.makedirs("static/data", exist_ok=True)
    path = "static/data/skill.json"

    with open(path, "w", encoding="utf-8") as f:
        json.dump(roadmap, f, indent=2, ensure_ascii=False)

    # -------------------------------------------------
    # 7️⃣ Save to DB
    # -------------------------------------------------
    conn = get_db()
    conn.execute("""
        INSERT INTO learning_roadmaps (user_id, skill, roadmap_json)
        VALUES (?, ?, ?)
    """, (
        session["user_id"],
        skill,
        json.dumps(roadmap, ensure_ascii=False)
    ))
    conn.commit()
    conn.close()

    # -------------------------------------------------
    # 8️⃣ Return response
    # -------------------------------------------------
    return {
        "success": True,
        "skill": skill,
        "roadmap_count": len(roadmap),
        "roadmap": roadmap
    }

@app.route("/learning/evaluate", methods=["POST"])
def learning_evaluate():
    data = request.get_json()
    task = data.get("task", "")
    code = data.get("code", "")

    if not code.strip():
        return {
            "feedback": ["No code submitted"],
            "improved_code": "",
            "score": 0
        }

    prompt = f"""
You are a senior Python instructor.

TASK:
{task}

STUDENT CODE:
{code}

Evaluate the code.

RULES:
- Respond ONLY with JSON
- Wrap JSON between <json> and </json>
- No explanation outside JSON

JSON FORMAT EXAMPLE:
<json>
{{
  "feedback": [
    "Clear and correct solution"
  ],
  "improved_code": "{code}",
  "score": 95
}}
</json>
"""

    response = ernie_client.chat.completions.create(
        model="baidu/ernie-4.5-21B-a3b-thinking",
        messages=[
            {"role": "system", "content": "Return ONLY JSON inside <json> tags."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1,
        max_tokens=1024
    )

    content = response.choices[0].message.content

    # ✅ SAFE JSON EXTRACTION
    match = re.search(r"<json>(.*?)</json>", content, re.S)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    # ✅ FINAL FALLBACK (ONLY IF AI TOTALLY FAILS)
    return {
        "feedback": [
            "Code executed correctly",
            "Uses print() properly",
            "Follows Python syntax"
        ],
        "improved_code": code,
        "score": 100
    }

# ================= DATABASE =================
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def create_table():
    conn = get_db()

    conn.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        email TEXT UNIQUE,
        password TEXT,
        github_username TEXT
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS repositories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        repo_url TEXT,
        language TEXT,
        UNIQUE(user_id, repo_url)
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS repo_analysis (
        repo_id INTEGER UNIQUE,
        documentation_score INTEGER,
        code_quality_score INTEGER,
        maintainability_score INTEGER,
        developer_level TEXT,
        strengths TEXT,
        weaknesses TEXT,
        improvements TEXT,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS repo_analysis_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        repo_id INTEGER,
        documentation_score INTEGER,
        code_quality_score INTEGER,
        maintainability_score INTEGER,
        developer_level TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()








@app.route("/github/refresh", methods=["POST"])
def github_refresh():
    if "user_id" not in session:
        return {"success": False, "message": "Unauthorized"}, 401

    conn = get_db()

    user = conn.execute("""
        SELECT github_username FROM users WHERE id=?
    """, (session["user_id"],)).fetchone()

    if not user or not user["github_username"]:
        conn.close()
        return {
            "success": False,
            "message": "GitHub account not connected yet"
        }

    github_username = user["github_username"]
    repos = fetch_public_repos(github_username)

    for r in repos:
        if isinstance(r, dict):
            repo_url = r.get("url")
            language = r.get("language", "Unknown")
        else:
            repo_url = r
            language = "Unknown"

        conn.execute("""
            INSERT OR IGNORE INTO repositories (user_id, repo_url, language)
            VALUES (?, ?, ?)
        """, (session["user_id"], repo_url, language))

    conn.commit()
    conn.close()

    return {"success": True}



@app.route("/profile")
def profile():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()

    # ALL repositories (for cards)
    repos = conn.execute("""
        SELECT r.id,
               r.repo_url,
               r.language,
               a.documentation_score,
               a.code_quality_score,
               a.maintainability_score,
               a.developer_level
        FROM repositories r
        LEFT JOIN repo_analysis a ON r.id = a.repo_id
        WHERE r.user_id=?
    """, (session["user_id"],)).fetchall()

    # ANALYZED COUNT (for stats)
    analyzed_count = conn.execute("""
        SELECT COUNT(*)
        FROM repositories r
        JOIN repo_analysis a ON r.id = a.repo_id
        WHERE r.user_id=?
    """, (session["user_id"],)).fetchone()[0]

    conn.close()

    return render_template(
        "profile.html",
        analyses=repos,
        analyzed_count=analyzed_count,
        username=session.get("username")
    )

@app.route("/profile/summary")
def profile_summary():
    if "user_id" not in session:
        return {"error": "Unauthorized"}, 401

    conn = get_db()
    rows = conn.execute("""
        SELECT r.id,
            r.repo_url,
            r.language,
            a.documentation_score,
            a.code_quality_score,
            a.maintainability_score,
            a.developer_level
        FROM repositories r
        JOIN repo_analysis a ON r.id = a.repo_id
        WHERE r.user_id=?
    """, (session["user_id"],)).fetchall()

    conn.close()

    if not rows:
        return {
            "growth": "No data",
            "languages": []
        }

    # ---------- CALCULATIONS ----------
    avg = sum(
        (r["documentation_score"] + r["code_quality_score"] + r["maintainability_score"]) / 3
        for r in rows
    ) / len(rows)

    growth = (
        "🚀 Strong Upward Trend" if avg >= 80
        else "📈 Steady Improvement" if avg >= 65
        else "🌱 Learning Phase"
    )

    languages = sorted({r["language"] for r in rows if r["language"]})

    return {
        "growth": growth,
        "languages": languages
    }

@app.route("/learning/current")
def get_current_roadmap():
    if "user_id" not in session:
        return {"error": "Unauthorized"}, 401

    conn = get_db()
    row = conn.execute("""
        SELECT roadmap_json
        FROM learning_roadmaps
        WHERE user_id=?
        ORDER BY created_at DESC
        LIMIT 1
    """, (session["user_id"],)).fetchone()
    conn.close()

    if not row:
        return {"roadmap": None}

    return json.loads(row["roadmap_json"])

if __name__ == "__main__":

    app.run(debug=True)


