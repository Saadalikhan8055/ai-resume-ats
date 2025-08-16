
import streamlit as st
import pandas as pd
from pathlib import Path
from html import escape


from nlp_utils import read_pdf, read_docx, load_skills, keyword_extract, match_skills, SbertScorer

st.set_page_config(
    page_title="AI Resume Screener (ATS)",
    page_icon="🧠",
    layout="wide",
)

HIDE_FOOTER = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
.skill-chip {
    display: inline-block;
    padding: 6px 10px;
    margin: 4px;
    border-radius: 999px;
    background: rgba(0, 122, 255, 0.12);
    border: 1px solid rgba(0, 122, 255, 0.25);
    font-size: 0.85rem;
}
.skill-chip.missing {
    background: rgba(255, 59, 48, 0.10);
    border-color: rgba(255, 59, 48, 0.25);
}
.small-muted { color: #7f8c8d; font-size: 0.85rem; }
.card {
    border-radius: 20px;
    padding: 18px;
    border: 1px solid rgba(0,0,0,0.06);
    box-shadow: 0 4px 24px rgba(0,0,0,0.05);
    background: white;
}
</style>
"""
st.markdown(HIDE_FOOTER, unsafe_allow_html=True)

@st.cache_resource(show_spinner=False)
def _load_scorer():
    return SbertScorer()

@st.cache_data(show_spinner=False)
def _load_skills_text():
    skills_text = Path("skills.yaml").read_text(encoding="utf-8")
    return skills_text

scorer = _load_scorer()
skills_text = _load_skills_text()
skills_by_bucket = load_skills(skills_text)

st.title("🧠 AI Resume Screener (ATS)")
st.write("Upload a resume and paste a job description to get a match score, detected skills, and gaps with recommendations.")

col1, col2 = st.columns([1,1])
with col1:
    resume_file = st.file_uploader("📄 Upload Resume (PDF or DOCX)", type=["pdf", "docx"])
with col2:
    jd_text = st.text_area("📝 Paste Job Description", height=220, placeholder="Paste the role description here...")

run = st.button("🚀 Analyze Resume", type="primary", use_container_width=True)

@st.cache_data(show_spinner=False)
def parse_resume(_resume_file):
    if not _resume_file:
        return ""
    ext = _resume_file.name.lower().split(".")[-1]
    content = _resume_file.read()
    if ext == "pdf":
        return read_pdf(content)
    elif ext == "docx":
        return read_docx(content)
    else:
        return ""

def _chips(items, missing=False):
    if not items:
        return ""
    cls = "skill-chip missing" if missing else "skill-chip"
    return " ".join([f"<span class='{cls}'>{escape(x)}</span>" for x in items])


st.divider()

if run:
    if not resume_file or not jd_text.strip():
        st.warning("Please upload a resume and paste a job description.")
        st.stop()

    with st.spinner("Parsing resume..."):
        resume_text = parse_resume(resume_file)

    if not resume_text:
        st.error("Could not read the file. Please upload a valid PDF or DOCX.")
        st.stop()

    with st.spinner("Scoring and extracting insights..."):
        match_score = scorer.score(resume_text, jd_text)
        resume_kw = keyword_extract(resume_text, max_k=20)
        jd_kw = keyword_extract(jd_text, max_k=20)
        found_by_bucket_resume, flat_resume_skills = match_skills(resume_text, skills_by_bucket)
        found_by_bucket_jd, flat_jd_skills = match_skills(jd_text, skills_by_bucket, fuzzy=False)
        missing_skills = sorted(list(set(flat_jd_skills) - set(flat_resume_skills)))
        matched_skills = sorted(list(set(flat_jd_skills).intersection(set(flat_resume_skills))))

    m1, m2, m3 = st.columns(3)
    m1.metric("Job Match Score", f"{match_score} / 100")
    m2.metric("Skills Matched", f"{len(matched_skills)}")
    m3.metric("Skills Missing", f"{len(missing_skills)}")

    st.divider()

    t1, t2, t3, t4 = st.tabs(["Overview", "Skills Map", "Texts", "Download Report"])

    with t1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("Summary")
        st.write("This analysis uses **semantic similarity (SBERT)** + **keyword/skill matching** to estimate fit. Improve the score by covering missing skills in your resume or tailoring your summary and experience bullets.")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("Top JD Keywords")
        st.markdown(_chips(jd_kw[:15]), unsafe_allow_html=True)
        st.subheader("Top Resume Keywords")
        st.markdown(_chips(resume_kw[:15]), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("Recommendations")
        if missing_skills:
            st.write("Focus on these **missing but requested** skills first:")
            st.markdown(_chips(missing_skills[:20], missing=True), unsafe_allow_html=True)
        else:
            st.write("Great! Your resume covers all detected JD skills.")
        st.markdown("</div>", unsafe_allow_html=True)

    with t2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("Skills by Bucket (Resume vs JD)")
        rows = []
        for bucket in skills_by_bucket.keys():
            rs = found_by_bucket_resume.get(bucket, [])
            js = found_by_bucket_jd.get(bucket, [])
            cov = len(set(rs).intersection(js))
            rows.append({
                "Bucket": bucket,
                "Resume skills": ", ".join(rs[:10]) if rs else "-",
                "JD skills": ", ".join(js[:10]) if js else "-",
                "Overlap count": cov
            })
        df = pd.DataFrame(rows).sort_values("Overlap count", ascending=False)
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("Matched & Missing Skills")
        st.write("**Matched:**")
        st.markdown(_chips(matched_skills), unsafe_allow_html=True)
        st.write("**Missing:**")
        st.markdown(_chips(missing_skills, missing=True), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with t3:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("Job Description (clean view)")
        st.text(jd_text)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("Resume (extracted text)")
        st.text(resume_text[:3000] + ("..." if len(resume_text) > 3000 else ""))
        st.caption("We limit what is displayed here for readability.")
        st.markdown("</div>", unsafe_allow_html=True)

    with t4:
        import json
        from datetime import datetime
        report = {
            "match_score": match_score,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "jd_keywords": jd_kw[:20],
            "resume_keywords": resume_kw[:20],
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "job_description": jd_text[:4000],
        }
        st.download_button(
            "📥 Download JSON Report",
            data=json.dumps(report, indent=2).encode("utf-8"),
            file_name="ats_report.json",
            mime="application/json",
            use_container_width=True
        )

with st.sidebar:
    st.header("How it works")
    st.write(
      #  "1) Extracts text from PDFs/DOCX 
       # "2) Uses SBERT for semantic similarity
        #"3) Matches skills using a curated list and keywords
        #"4) Highlights missing skills and gives recommendations"
    )
    st.write("---")
    st.caption("Tip: Tailor your resume to the JD for best results.")
