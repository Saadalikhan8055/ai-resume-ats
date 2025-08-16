# AI Resume ATS Analyzer

🚀 An AI-powered ATS Resume Analyzer built with **Python** and **Streamlit** that evaluates resumes against job descriptions using **NLP** and **Sentence-BERT**.  

## ✨ Features
- 📂 Upload resume (PDF/DOCX) and job description (text/ JD file)  
- 🧠 Extracts keywords, skills, and entities using NLP  
- 📊 Calculates ATS match score (%)  
- 🔍 Highlights missing skills and keywords  
- 🎯 Provides actionable insights to improve your resume  

## 🛠 Tech Stack
- Python  
- Streamlit  
- NLP (Spacy, SBERT)  
- YAML for skills database  

## ⚡ How to Run Locally
```bash
# Clone the repository
git clone https://github.com/saadalikhan8055/ai-resume-ats.git
cd ai-resume-ats

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
