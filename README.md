# 🧠 AI Resume ATS Analyzer

An AI-powered Applicant Tracking System (ATS) Resume Analyzer built with **Python** and **Streamlit** that evaluates resumes against job descriptions using advanced **NLP** and **Semantic similarity** (Sentence-BERT).

Maximize your resume's potential by getting insights into how well your background matches job requirements, and receive actionable recommendations for improvement.

---

## ✨ Key Features

- 📄 **Multi-format Resume Upload**: Support for PDF and DOCX documents
- 📝 **Job Description Analysis**: Paste or input job requirements directly
- 📊 **AI-Powered Matching Score**: Semantic similarity-based ATS scoring (0-100)
- 🎯 **Skill Detection & Matching**: Identifies matched and missing skills by category
- 🔍 **Keyword Extraction**: Extracts top keywords from both resume and job description
- 📋 **Skill Categorization**: Organizes skills into 6 categories:
  - Core ML (machine learning, deep learning, etc.)
  - NLP (natural language processing)
  - Computer Vision (CV)
  - Data Engineering (Python, SQL, ETL, etc.)
  - Infrastructure (Docker, Kubernetes, Cloud platforms)
  - Tools & Languages (Git, Linux, Bash, etc.)
- 💡 **Smart Recommendations**: Highlights critical missing skills with priority suggestions
- 📥 **Report Export**: Download detailed analysis as JSON for record-keeping
- 🎨 **Interactive UI**: Clean, intuitive interface with tabbed analysis sections

---

## 🛠 Tech Stack

| Component | Technology |
|-----------|-----------|
| **Frontend** | Streamlit 1.35+ |
| **Semantic Scoring** | Sentence-BERT (all-MiniLM-L6-v2) |
| **Keyword Extraction** | YAKE |
| **Skill Matching** | RapidFuzz (fuzzy matching) |
| **Document Parsing** | pdfminer.six, python-docx |
| **ML/Data** | PyTorch, scikit-learn, pandas, numpy |
| **Config** | PyYAML |

---

## 📦 Installation

### Prerequisites
- Python 3.8+
- pip package manager

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/saadalikhan8055/ai-resume-ats.git
cd ai-resume-ats
```

2. **Create a virtual environment** (recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

---

## 🚀 Usage

### Run the Application
```bash
streamlit run app.py
```

The app will open in your browser (typically at `http://localhost:8501`)

### Workflow
1. Upload your resume (PDF or DOCX format)
2. Paste the job description in the text area
3. Click **"🚀 Analyze Resume"** to generate insights
4. Review the results across 4 tabs:
   - **Overview**: Match score, top keywords, recommendations
   - **Skills Map**: Detailed skill breakdown by category
   - **Texts**: Raw extracted text for verification
   - **Download Report**: Export results as JSON

---

## 📁 Project Structure

```
.
├── app.py              # Main Streamlit application & UI
├── nlp_utils.py        # NLP utilities & core logic
├── skills.yaml         # Curated skills database (6 categories)
├── requirements.txt    # Python dependencies
├── README.md           # This file
└── __pycache__/        # Python cache
```

### File Descriptions

| File | Purpose |
|------|---------|
| **app.py** | Streamlit UI, file upload, caching, results display, report generation |
| **nlp_utils.py** | PDF/DOCX parsing, skill loading, keyword extraction, fuzzy matching, SBERT scoring |
| **skills.yaml** | Structured skills database (100+ skills across 6 ML/data tech categories) |
| **requirements.txt** | All Python package dependencies with versions |

---

## 🔍 How It Works

### Scoring Algorithm

The **Match Score** (0-100) is calculated using:

1. **Semantic Similarity (60% weight)**
   - Encodes resume and JD into embeddings using Sentence-BERT
   - Computes cosine similarity between embeddings
   - Converts similarity to 0-100 score

2. **Skill Matching (40% weight)**
   - Extracts skills from job description
   - Matches against resume using:
     - Exact string matching
     - Fuzzy matching (90%+ similarity threshold via RapidFuzz)
   - Calculates overlap ratio

### Skill Detection
- Skills are organized in 6 buckets (ML, NLP, CV, Data, Infrastructure, Tools)
- Both exact keyword and fuzzy matching for flexibility
- Deduplication and normalization of matched skills

### Recommendations
- **Matched Skills**: Skills found in both resume and JD
- **Missing Skills**: Critical skills in JD but absent from resume
- **Priority Order**: Missing skills shown by frequency/importance

---

## 📊 Dependencies

Core packages:
- `streamlit` - Web app framework
- `sentence-transformers` - Semantic embeddings (SBERT)
- `torch / torchvision / torchaudio` - Deep learning backend
- `pdfminer.six` - PDF text extraction
- `python-docx` - DOCX parsing
- `yake` - Keyword extraction
- `rapidfuzz` - Fuzzy string matching
- `pandas` - Data manipulation
- `pyyaml` - YAML config parsing
- `numpy`, `scikit-learn`, `spacy` - NLP/ML utilities

---

## 💡 Tips for Best Results

1. **Resume Content**: Ensure your resume includes:
   - Specific technology names and tools used
   - Quantified accomplishments
   - Relevant certifications

2. **Job Description**: Use complete JD text including:
   - Required skills section
   - Responsibilities
   - Nice-to-have qualifications

3. **Interpreting Results**:
   - Score 70+: Strong match
   - Score 50-70: Moderate match (focus on missing skills)
   - Score <50: Consider tailoring resume or exploring different roles

4. **Improving Match Score**:
   - Add missing high-priority skills to your resume
   - Highlight relevant projects and experience
   - Use specific tool/framework names (e.g., "PyTorch" vs. "deep learning")

---

## 🔧 Configuration

The skills database can be customized by editing `skills.yaml`. Add new skills or categories as needed:

```yaml
category_name:
  - skill1
  - skill2
  - skill3
```

---

## 📄 License

This project is open source and available under the MIT License.

---

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs or issues
- Suggest new features
- Improve documentation
- Add new skills to the database
- Enhance the scoring algorithm

---

## 📧 Support

For questions, issues, or feedback, please open an issue in the GitHub repository.

---

**Made with ❤️ to help you land your dream job!**
