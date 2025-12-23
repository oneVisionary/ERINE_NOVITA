from openai import OpenAI
import os
import requests
import zipfile
import io
from pathlib import Path
from dotenv import load_dotenv
import json
import re

# ---------------- LOAD ENV ----------------
load_dotenv()

NOVITA_API_KEY = os.getenv("NOVITA_API_KEY")
if not NOVITA_API_KEY:
    raise RuntimeError("NOVITA_API_KEY not set in .env")

client = OpenAI(
    api_key=NOVITA_API_KEY,
    base_url="https://api.novita.ai/openai"
)

# ---------------- CONSTANTS ----------------
MAX_FILES = 15
MAX_FILE_CHARS = 1500

# ---------------- HELPERS ----------------

def parse_github_url(url: str):
    if "github.com" not in url:
        raise ValueError("Invalid GitHub URL")

    url = url.rstrip("/")
    if url.endswith(".git"):
        url = url[:-4]

    parts = url.split("/")
    return parts[-2], parts[-1]


def download_repo_zip(owner, repo):
    for branch in ("main", "master"):
        zip_url = f"https://github.com/{owner}/{repo}/archive/refs/heads/{branch}.zip"
        r = requests.get(zip_url, timeout=30)
        if r.status_code == 200:
            return r.content

    raise RuntimeError("Could not download repository ZIP")


def extract_repo_summary(zip_bytes):
    summary = {
        "total_files": 0,
        "file_types": {},
        "readme": "",
        "code_samples": []
    }

    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
        files = [f for f in z.namelist() if not f.endswith("/")]
        summary["total_files"] = len(files)

        for f in files:
            ext = Path(f).suffix.lower()
            summary["file_types"][ext] = summary["file_types"].get(ext, 0) + 1

        for f in files:
            if Path(f).name.lower().startswith("readme"):
                summary["readme"] = z.read(f).decode("utf-8", errors="ignore")[:3000]
                break

        source_exts = {".py", ".js", ".ts", ".java", ".cpp", ".c", ".go", ".rs"}
        for f in files:
            if Path(f).suffix.lower() in source_exts:
                try:
                    content = z.read(f).decode("utf-8", errors="ignore")
                    summary["code_samples"].append({
                        "file": f,
                        "content": content[:MAX_FILE_CHARS]
                    })
                except:
                    pass

            if len(summary["code_samples"]) >= MAX_FILES:
                break

    return summary


def build_prompt(repo_url, summary):
    return f"""
You are a senior software engineer performing an AI-assisted review of a public GitHub repository.

Repository URL:
{repo_url}

Total files: {summary['total_files']}
File types:
{json.dumps(summary['file_types'], indent=2)}

README:
{summary['readme'] or "No README"}

Code Samples:
{json.dumps(summary['code_samples'], indent=2)}

Return ONLY valid JSON:

{{
  "documentation_score": 0-100,
  "code_quality_score": 0-100,
  "maintainability_score": 0-100,
  "estimated_developer_level": "beginner | intermediate | advanced",
  "strengths": [],
  "weaknesses": [],
  "improvement_suggestions": []
}}
"""


def extract_json(text):
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        raise RuntimeError("No JSON found in AI response")
    return json.loads(match.group())


# ---------------- MAIN API ----------------

def analyze_repo(repo_url):
    owner, repo = parse_github_url(repo_url)
    zip_bytes = download_repo_zip(owner, repo)
    summary = extract_repo_summary(zip_bytes)
    prompt = build_prompt(repo_url, summary)

    response = client.chat.completions.create(
        model="baidu/ernie-4.5-vl-424b-a47b",
        messages=[
            {"role": "system", "content": "You are a professional GitHub repository reviewer."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
        max_tokens=3000
    )

    raw = response.choices[0].message.content.strip()
    return extract_json(raw)
