
# 🧠 AI-Powered Resume Screener (ATS)

A clean end-to-end project for ML Engineering portfolios: upload a resume (PDF/DOCX), paste a Job Description (JD), and get:
- ✅ **Job Match Score** (SBERT cosine similarity)
- ✅ **Matched & Missing Skills**
- ✅ **Top Keywords** (YAKE)
- ✅ **Downloadable JSON report**
- ✅ **Modern Streamlit UI** with tabs, metrics, and chips

---

## ⚙️ Tech Stack
- **NLP/Embeddings:** Sentence Transformers (`all-MiniLM-L6-v2`)
- **Keyword Extraction:** YAKE
- **Parsing:** pdfminer.six, python-docx
- **UI:** Streamlit
- **Skill Matching:** curated `skills.yaml` + fuzzy matching

---

## 🚀 Quickstart

```bash
# 1) Create and activate a virtual environment (Windows PowerShell)
py -m venv .venv
.venv\Scripts\Activate.ps1

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate

# 2) Install deps
pip install -r requirements.txt

# 3) (Optional) spaCy model for better NLP later if you extend the app
python -m spacy download en_core_web_sm

# 4) Run the app
streamlit run app.py
```

App opens at http://localhost:8501

---

## 🧪 How to Use
1. Upload **PDF or DOCX** resume.
2. Paste a **Job Description**.
3. Click **Analyze Resume**.
4. Check **Overview, Skills Map, Texts, Download** tabs.
5. Download the **JSON report** and share with recruiters or attach in applications.

---

## 📂 Project Structure
```
ai_resume_ats/
├── app.py
├── nlp_utils.py
├── skills.yaml
├── requirements.txt
└── README.md
```

---

## 🧰 Notes & Customization
- Add domain-specific skills to `skills.yaml` (e.g., fintech, healthcare, LLM ops).
- Tweak the UI chips/metrics and thresholds.
- Replace or augment the skill matcher with a trained NER model if desired.
- Persist results to a database (SQLite/Postgres) and add authentication for a multi-user dashboard.

---

## ☁️ Deploy (Streamlit Community Cloud)
1. Push this folder to GitHub.
2. On Streamlit Cloud, create a new app → select your repo → set `app.py` as entry.
3. Add the following to **Secrets** if needed (none required now).
4. Deploy. The app will build and run using `requirements.txt`.

---

## 📄 License
MIT
