import json
from datetime import datetime
from html import escape
from pathlib import Path
import time

import pandas as pd
import streamlit as st

from nlp_utils import SbertScorer, keyword_extract, load_skills, match_skills, read_docx, read_pdf


st.set_page_config(
    page_title="AI Resume Screener (ATS)",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

THEME = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@400;500&display=swap');

:root {
    --bg: #0b1020;
    --panel: rgba(12, 18, 34, 0.72);
    --panel-strong: rgba(15, 23, 42, 0.92);
    --border: rgba(148, 163, 184, 0.16);
    --text: #e5eefb;
    --muted: #9fb0c9;
    --accent: #7dd3fc;
    --accent-2: #34d399;
    --accent-3: #f59e0b;
    --danger: #fb7185;
    --shadow: 0 22px 60px rgba(2, 8, 23, 0.40);
}

#MainMenu, footer { visibility: hidden; }

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at top left, rgba(45, 212, 191, 0.14), transparent 28%),
        radial-gradient(circle at top right, rgba(125, 211, 252, 0.15), transparent 24%),
        radial-gradient(circle at bottom left, rgba(59, 130, 246, 0.10), transparent 22%),
        linear-gradient(180deg, #050816 0%, #0b1020 38%, #0f172a 100%);
    color: var(--text);
}

.app-shell {
    position: relative;
    padding-top: 0.5rem;
}

.app-shell::before,
.app-shell::after {
    content: "";
    position: fixed;
    z-index: 0;
    border-radius: 999px;
    filter: blur(40px);
    opacity: 0.32;
    pointer-events: none;
    animation: float 16s ease-in-out infinite;
}

.app-shell::before {
    width: 240px;
    height: 240px;
    top: 7%;
    right: 6%;
    background: rgba(56, 189, 248, 0.25);
}

.app-shell::after {
    width: 180px;
    height: 180px;
    bottom: 10%;
    left: 8%;
    background: rgba(52, 211, 153, 0.18);
    animation-delay: -6s;
}

@keyframes float {
    0%, 100% { transform: translate3d(0, 0, 0) scale(1); }
    50% { transform: translate3d(0, -16px, 0) scale(1.05); }
}

@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

.hero {
    position: relative;
    overflow: hidden;
    padding: 2rem 2rem 1.6rem 2rem;
    border: 1px solid rgba(148, 163, 184, 0.18);
    border-radius: 28px;
    background: linear-gradient(135deg, rgba(15, 23, 42, 0.92), rgba(8, 15, 33, 0.78));
    box-shadow: var(--shadow);
}

.hero::after {
    content: "";
    position: absolute;
    inset: 0;
    background: linear-gradient(120deg, rgba(125, 211, 252, 0.08), transparent 30%, rgba(52, 211, 153, 0.08));
    pointer-events: none;
}

.eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.4rem 0.8rem;
    border-radius: 999px;
    border: 1px solid rgba(125, 211, 252, 0.22);
    background: rgba(125, 211, 252, 0.08);
    color: #d7f3ff;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.76rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

.hero h1 {
    margin-bottom: 0.2rem;
    font-size: clamp(2.3rem, 4vw, 4.3rem);
    line-height: 1.02;
    letter-spacing: -0.04em;
    color: #f8fbff;
}

.hero-copy {
    max-width: 760px;
    color: var(--muted);
    font-size: 1.03rem;
    line-height: 1.7;
}

.hero-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 0.9rem;
    margin-top: 1.4rem;
}

.mini-card {
    padding: 1rem 1.05rem;
    border-radius: 18px;
    border: 1px solid rgba(148, 163, 184, 0.14);
    background: rgba(15, 23, 42, 0.58);
    backdrop-filter: blur(14px);
}

.mini-card .label {
    color: var(--muted);
    font-size: 0.8rem;
    margin-bottom: 0.3rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

.mini-card .value {
    color: #ffffff;
    font-size: 1.05rem;
    font-weight: 700;
}

.mini-card .sub {
    color: #c8d4e7;
    font-size: 0.9rem;
    margin-top: 0.25rem;
}

.section-panel {
    position: relative;
    padding: 1.4rem;
    border: 1px solid var(--border);
    border-radius: 24px;
    background: linear-gradient(180deg, rgba(15, 23, 42, 0.88), rgba(9, 14, 29, 0.78));
    box-shadow: var(--shadow);
    backdrop-filter: blur(18px);
    margin-top: 1rem;
    animation: fadeInUp 0.45s ease both;
}

.section-panel h2, .section-panel h3 {
    color: #f8fbff;
}

.section-panel p, .section-panel li, .section-panel .stMarkdown, .section-panel .stCaption {
    color: #d2dded;
}

.skill-chip {
    display: inline-flex;
    align-items: center;
    padding: 0.45rem 0.7rem;
    margin: 0.25rem 0.35rem 0.25rem 0;
    border-radius: 999px;
    background: linear-gradient(135deg, rgba(125, 211, 252, 0.16), rgba(52, 211, 153, 0.13));
    border: 1px solid rgba(125, 211, 252, 0.18);
    color: #e9f5ff;
    font-size: 0.84rem;
    box-shadow: 0 8px 20px rgba(2, 8, 23, 0.22);
    transition: transform 0.2s ease, border-color 0.2s ease, background 0.2s ease;
}

.skill-chip:hover {
    transform: translateY(-1px);
    border-color: rgba(125, 211, 252, 0.42);
}

.skill-chip.missing {
    background: linear-gradient(135deg, rgba(251, 113, 133, 0.16), rgba(248, 113, 113, 0.10));
    border-color: rgba(251, 113, 133, 0.26);
}

.small-muted {
    color: #9fb0c9;
    font-size: 0.88rem;
}

.card {
    border-radius: 22px;
    padding: 1.2rem 1.2rem 0.9rem 1.2rem;
    margin-bottom: 1rem;
    border: 1px solid rgba(148, 163, 184, 0.14);
    background: linear-gradient(180deg, rgba(15, 23, 42, 0.86), rgba(10, 15, 31, 0.76));
    box-shadow: 0 14px 40px rgba(2, 8, 23, 0.24);
}

.stTabs [data-baseweb="tab-list"] {
    gap: 0.5rem;
    background: rgba(15, 23, 42, 0.55);
    padding: 0.45rem;
    border-radius: 16px;
    border: 1px solid rgba(148, 163, 184, 0.14);
}

.stTabs [data-baseweb="tab"] {
    border-radius: 12px;
    padding: 0.55rem 1rem;
    color: #c7d4e7;
    background: transparent;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, rgba(125, 211, 252, 0.22), rgba(52, 211, 153, 0.16));
    color: #ffffff;
}

.stButton > button {
    width: 100%;
    border-radius: 16px;
    border: 1px solid rgba(125, 211, 252, 0.25);
    background: linear-gradient(135deg, #0ea5e9, #14b8a6);
    color: white;
    font-weight: 700;
    padding: 0.8rem 1rem;
    box-shadow: 0 14px 30px rgba(14, 165, 233, 0.28);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 18px 36px rgba(14, 165, 233, 0.34);
}

.stButton > button:active {
    transform: scale(0.98);
    box-shadow: 0 0 0 4px rgba(56, 189, 248, 0.16), 0 14px 30px rgba(14, 165, 233, 0.28);
}

.stDownloadButton > button {
    width: 100%;
    border-radius: 16px;
    border: 1px solid rgba(52, 211, 153, 0.24);
    background: linear-gradient(135deg, #0f766e, #14532d);
    color: white;
    font-weight: 700;
    padding: 0.8rem 1rem;
}

.stTextInput input, .stTextArea textarea {
    background: rgba(15, 23, 42, 0.7) !important;
    color: #f8fbff !important;
    border-radius: 16px !important;
    border: 1px solid rgba(148, 163, 184, 0.18) !important;
}

.sidebar-panel {
    padding: 1rem 1rem 1.2rem 1rem;
    border-radius: 22px;
    border: 1px solid rgba(148, 163, 184, 0.14);
    background: linear-gradient(180deg, rgba(15, 23, 42, 0.84), rgba(9, 14, 29, 0.72));
    box-shadow: 0 16px 42px rgba(2, 8, 23, 0.24);
}

.sidebar-badge {
    display: inline-flex;
    padding: 0.34rem 0.64rem;
    border-radius: 999px;
    background: rgba(52, 211, 153, 0.1);
    border: 1px solid rgba(52, 211, 153, 0.18);
    color: #d7ffef;
    font-size: 0.78rem;
    margin-bottom: 0.8rem;
}

.result-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 0.9rem;
    margin: 0.8rem 0 0.4rem 0;
}

.result-stat {
    padding: 1rem;
    border-radius: 18px;
    background: linear-gradient(180deg, rgba(125, 211, 252, 0.12), rgba(15, 23, 42, 0.72));
    border: 1px solid rgba(125, 211, 252, 0.16);
}

.result-stat .label {
    color: var(--muted);
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

.result-stat .value {
    color: white;
    font-size: 1.8rem;
    font-weight: 800;
    margin-top: 0.2rem;
}

.result-stat .helper {
    color: #c8d4e7;
    font-size: 0.9rem;
    margin-top: 0.25rem;
}

.result-badge-row {
    display: flex;
    flex-wrap: wrap;
    gap: 0.45rem;
}

.result-badge {
    padding: 0.38rem 0.65rem;
    border-radius: 999px;
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.1);
    color: #e9f5ff;
    font-size: 0.82rem;
}

.result-badge.good {
    background: rgba(52, 211, 153, 0.11);
    border-color: rgba(52, 211, 153, 0.18);
}

.result-badge.warn {
    background: rgba(251, 191, 36, 0.11);
    border-color: rgba(251, 191, 36, 0.18);
}

.verdict-shell {
    display: grid;
    grid-template-columns: minmax(0, 1.5fr) minmax(0, 1fr);
    gap: 1rem;
    align-items: stretch;
    margin-top: 1rem;
}

.verdict-card {
    padding: 1.2rem;
    border-radius: 20px;
    border: 1px solid rgba(148, 163, 184, 0.14);
    background: linear-gradient(180deg, rgba(15, 23, 42, 0.92), rgba(9, 14, 29, 0.84));
    box-shadow: 0 16px 42px rgba(2, 8, 23, 0.28);
}

.verdict-card .title {
    color: #f8fbff;
    font-size: 1.05rem;
    font-weight: 700;
    margin-bottom: 0.35rem;
}

.verdict-card .subtitle {
    color: #c8d4e7;
    font-size: 0.92rem;
    line-height: 1.6;
    margin-bottom: 1rem;
}

.verdict-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    padding: 0.45rem 0.75rem;
    border-radius: 999px;
    font-size: 0.82rem;
    font-weight: 700;
    letter-spacing: 0.03em;
}

.verdict-pill.good {
    background: rgba(52, 211, 153, 0.14);
    border: 1px solid rgba(52, 211, 153, 0.25);
    color: #d8ffee;
}

.verdict-pill.warn {
    background: rgba(251, 191, 36, 0.14);
    border: 1px solid rgba(251, 191, 36, 0.25);
    color: #fff4d1;
}

.verdict-pill.info {
    background: rgba(125, 211, 252, 0.14);
    border: 1px solid rgba(125, 211, 252, 0.25);
    color: #e1f6ff;
}

.score-track {
    margin-top: 0.85rem;
    width: 100%;
    height: 14px;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.08);
    overflow: hidden;
    border: 1px solid rgba(255, 255, 255, 0.08);
}

.score-fill {
    height: 100%;
    border-radius: inherit;
    background: linear-gradient(90deg, #22c55e 0%, #38bdf8 55%, #0ea5e9 100%);
    box-shadow: 0 0 22px rgba(56, 189, 248, 0.35);
}

.score-meta {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 0.75rem;
    margin-top: 0.7rem;
    color: #c8d4e7;
    font-size: 0.86rem;
}

.action-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 0.9rem;
}

.action-card {
    padding: 1rem;
    border-radius: 18px;
    border: 1px solid rgba(148, 163, 184, 0.14);
    background: rgba(15, 23, 42, 0.58);
}

.action-card .heading {
    color: #f8fbff;
    font-weight: 700;
    margin-bottom: 0.3rem;
}

.action-card .detail {
    color: #c8d4e7;
    font-size: 0.9rem;
    line-height: 1.55;
}

.bucket-bar {
    margin-top: 0.35rem;
    width: 100%;
    height: 10px;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.06);
    overflow: hidden;
}

.bucket-fill {
    height: 100%;
    border-radius: inherit;
    background: linear-gradient(90deg, rgba(34, 197, 94, 0.95), rgba(125, 211, 252, 0.92));
}

.launch-strip {
    margin: 0.75rem 0 0.25rem 0;
    padding: 0.9rem 1rem;
    border-radius: 18px;
    border: 1px solid rgba(125, 211, 252, 0.16);
    background: linear-gradient(135deg, rgba(14, 165, 233, 0.10), rgba(52, 211, 153, 0.08));
    box-shadow: 0 14px 30px rgba(2, 8, 23, 0.18);
    animation: launchPulse 0.9s ease-in-out 2;
}

.loading-shell {
    margin: 0.75rem 0 0.25rem 0;
    padding: 1rem 1rem 0.95rem 1rem;
    border-radius: 22px;
    border: 1px solid rgba(125, 211, 252, 0.18);
    background: linear-gradient(135deg, rgba(15, 23, 42, 0.92), rgba(12, 18, 34, 0.82));
    box-shadow: 0 18px 40px rgba(2, 8, 23, 0.24);
    overflow: hidden;
}

.loading-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.75rem;
}

.loading-title {
    color: #f8fbff;
    font-size: 1rem;
    font-weight: 700;
    margin-bottom: 0.25rem;
}

.loading-detail {
    color: #c8d4e7;
    font-size: 0.9rem;
}

.loading-dots {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
}

.loading-dots span {
    width: 8px;
    height: 8px;
    border-radius: 999px;
    background: linear-gradient(180deg, #7dd3fc, #34d399);
    animation: dotBounce 0.9s ease-in-out infinite;
}

.loading-dots span:nth-child(2) { animation-delay: 0.12s; }
.loading-dots span:nth-child(3) { animation-delay: 0.24s; }

.loading-bar {
    position: relative;
    margin-top: 0.9rem;
    width: 100%;
    height: 12px;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.08);
    overflow: hidden;
}

.loading-bar::after {
    content: "";
    position: absolute;
    inset: 0;
    width: 42%;
    border-radius: inherit;
    background: linear-gradient(90deg, rgba(52, 211, 153, 0.15), rgba(125, 211, 252, 0.92), rgba(14, 165, 233, 0.22));
    box-shadow: 0 0 18px rgba(125, 211, 252, 0.35);
    animation: loadingSweep 1.15s linear infinite;
}

.loading-step {
    margin-top: 0.75rem;
    color: #e5eefb;
    font-size: 0.88rem;
    letter-spacing: 0.02em;
}

.launch-strip .headline {
    color: #f8fbff;
    font-weight: 700;
    margin-bottom: 0.25rem;
}

.launch-strip .detail {
    color: #c8d4e7;
    font-size: 0.9rem;
}

@keyframes launchPulse {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-2px); }
}

@keyframes dotBounce {
    0%, 80%, 100% { transform: translateY(0); opacity: 0.55; }
    40% { transform: translateY(-5px); opacity: 1; }
}

@keyframes loadingSweep {
    0% { transform: translateX(-18%); }
    100% { transform: translateX(230%); }
}

@media (max-width: 1100px) {
    .hero-grid, .result-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    .verdict-shell, .action-grid { grid-template-columns: 1fr; }
}

@media (max-width: 720px) {
    .hero, .section-panel, .card { padding: 1rem; }
    .hero-grid, .result-grid { grid-template-columns: 1fr; }
}
</style>
"""

st.markdown(THEME, unsafe_allow_html=True)


def _chips(items, missing=False):
    if not items:
        return ""
    cls = "skill-chip missing" if missing else "skill-chip"
    return " ".join([f"<span class='{cls}'>{escape(x)}</span>" for x in items])


def _score_band(score):
    if score >= 80:
        return "Excellent fit", "good", "The resume aligns strongly with the role."
    if score >= 65:
        return "Strong fit", "info", "There is solid alignment, with a few targeted gaps."
    if score >= 45:
        return "Moderate fit", "warn", "The resume needs role-specific tailoring to compete well."
    return "Low fit", "warn", "The current resume is missing several core signals from the JD."


def _action_texts(missing_skills, resume_kw, jd_kw):
    focus = ", ".join(missing_skills[:5]) if missing_skills else "none"
    resume_focus = ", ".join(resume_kw[:5]) if resume_kw else "-"
    jd_focus = ", ".join(jd_kw[:5]) if jd_kw else "-"
    return focus, resume_focus, jd_focus


def _render_hero():
    st.markdown(
        """
        <div class="hero">
            <div class="eyebrow">ATS intelligence dashboard</div>
            <h1>Screen resumes with a premium, recruiter-ready experience.</h1>
            <p class="hero-copy">
                Upload a resume, paste a job description, and get a polished analysis with semantic scoring,
                skill overlap, missing-skill guidance, and exportable insights. The interface is built to feel
                modern, credible, and presentation-ready.
            </p>
            <div class="hero-grid">
                <div class="mini-card">
                    <div class="label">Semantic scoring</div>
                    <div class="value">SBERT</div>
                    <div class="sub">Meaning-aware fit analysis</div>
                </div>
                <div class="mini-card">
                    <div class="label">Skill intelligence</div>
                    <div class="value">Curated buckets</div>
                    <div class="sub">ATS-friendly matching cues</div>
                </div>
                <div class="mini-card">
                    <div class="label">Output</div>
                    <div class="value">Exportable report</div>
                    <div class="sub">Shareable JSON summary</div>
                </div>
                <div class="mini-card">
                    <div class="label">Layout</div>
                    <div class="value">Responsive UI</div>
                    <div class="sub">Desktop and mobile friendly</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


@st.cache_resource(show_spinner=False)
def _load_scorer():
    return SbertScorer()


@st.cache_data(show_spinner=False)
def _load_skills_text():
    return Path("skills.yaml").read_text(encoding="utf-8")


@st.cache_data(show_spinner=False)
def parse_resume(_resume_file):
    if not _resume_file:
        return ""
    ext = _resume_file.name.lower().split(".")[-1]
    content = _resume_file.read()
    if ext == "pdf":
        return read_pdf(content)
    if ext == "docx":
        return read_docx(content)
    return ""


def _open_panel():
    st.markdown("<div class='section-panel'>", unsafe_allow_html=True)


def _close_panel():
    st.markdown("</div>", unsafe_allow_html=True)


scorer = _load_scorer()
skills_text = _load_skills_text()
skills_by_bucket = load_skills(skills_text)

st.markdown("<div class='app-shell'>", unsafe_allow_html=True)
_render_hero()

st.write("")
st.caption("Upload a resume and paste a job description to generate a high-signal ATS style review.")

col1, col2 = st.columns([1, 1])
with col1:
    resume_file = st.file_uploader("Resume source", type=["pdf", "docx"], label_visibility="collapsed")
    st.markdown("<div class='small-muted'>Accepted formats: PDF and DOCX</div>", unsafe_allow_html=True)
with col2:
    jd_text = st.text_area(
        "Job description",
        height=240,
        placeholder="Paste the role description here...",
        label_visibility="collapsed",
    )

st.write("")
run = st.button("Analyze Resume", type="primary", use_container_width=True)

if run:
    loading_placeholder = st.empty()
    progress_placeholder = st.empty()
    scan_states = [
        (14, "Extracting resume text"),
        (38, "Comparing semantic fit"),
        (66, "Matching skills and keywords"),
        (100, "Building results"),
    ]
    for percent, message in scan_states:
        loading_placeholder.markdown(
            f"""
            <div class='loading-shell'>
                <div class='loading-top'>
                    <div>
                        <div class='loading-title'>Analyzing resume</div>
                        <div class='loading-detail'>Processing your file and job description now.</div>
                    </div>
                    <div class='loading-dots' aria-hidden='true'><span></span><span></span><span></span></div>
                </div>
                <div class='loading-bar'></div>
                <div class='loading-step'>{message}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        progress_placeholder.progress(percent, text=message)
        time.sleep(0.12)
    loading_placeholder.empty()
    progress_placeholder.empty()

st.divider()

if run:
    if not resume_file or not jd_text.strip():
        st.warning("Please upload a resume and paste a job description.")
        st.stop()

    with st.spinner("Reading and normalizing resume text..."):
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

    _open_panel()
    st.markdown("## Executive Snapshot")
    st.write("A concise, visually polished overview of the resume-to-role fit.")
    verdict_text, verdict_tone, verdict_blurb = _score_band(match_score)
    missing_focus, resume_focus, jd_focus = _action_texts(missing_skills, resume_kw, jd_kw)
    st.markdown(
        f"""
        <div class="result-grid">
            <div class="result-stat">
                <div class="label">Job match score</div>
                <div class="value">{match_score}</div>
                <div class="helper">Out of 100 using semantic similarity</div>
            </div>
            <div class="result-stat">
                <div class="label">Skills matched</div>
                <div class="value">{len(matched_skills)}</div>
                <div class="helper">Direct overlap with the JD</div>
            </div>
            <div class="result-stat">
                <div class="label">Skills missing</div>
                <div class="value">{len(missing_skills)}</div>
                <div class="helper">Areas to tailor before applying</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
        <div class="verdict-shell">
            <div class="verdict-card">
                <div class="title">Fit verdict</div>
                <div class="subtitle">{verdict_blurb}</div>
                <span class="verdict-pill {verdict_tone}">{verdict_text}</span>
                <div class="score-track">
                    <div class="score-fill" style="width: {match_score}%"></div>
                </div>
                <div class="score-meta">
                    <span>Match confidence</span>
                    <span>{match_score}%</span>
                </div>
            </div>
            <div class="verdict-card">
                <div class="title">Readout</div>
                <div class="subtitle">A quick framing of what is working and where to tune the resume.</div>
                <span class="verdict-pill info">Resume keywords: {len(resume_kw[:20])}</span>
                <div style="height: 0.5rem;"></div>
                <span class="verdict-pill info">JD keywords: {len(jd_kw[:20])}</span>
                <div style="height: 0.5rem;"></div>
                <span class="verdict-pill warn">Priority gap: {missing_focus if missing_focus else 'No major gaps detected'}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div class='result-badge-row'>"
        "<span class='result-badge good'>Resume parsed successfully</span>"
        "<span class='result-badge'>SBERT scoring active</span>"
        f"<span class='result-badge'>{len(jd_kw[:20])} JD keywords detected</span>"
        f"<span class='result-badge'>{len(resume_kw[:20])} resume keywords detected</span>"
        "</div>",
        unsafe_allow_html=True,
    )
    _close_panel()

    st.divider()

    t1, t2, t3, t4 = st.tabs(["Overview", "Skills Map", "Text Views", "Export"])

    with t1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("Summary")
        st.write(
            "This analysis blends semantic similarity with curated skill matching to estimate ATS fit. "
            "Use the missing skills list to tighten the resume narrative before applying."
        )
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("Next edits")
        st.markdown(
            f"""
            <div class="action-grid">
                <div class="action-card">
                    <div class="heading">Priority skills</div>
                    <div class="detail">{missing_focus if missing_focus else 'No priority gaps detected. Focus on framing measurable impact.'}</div>
                </div>
                <div class="action-card">
                    <div class="heading">Resume signal</div>
                    <div class="detail">Top resume themes: {resume_focus}</div>
                </div>
                <div class="action-card">
                    <div class="heading">JD signal</div>
                    <div class="detail">Top role themes: {jd_focus}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
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
            st.write("Focus on these missing but requested skills first:")
            st.markdown(_chips(missing_skills[:20], missing=True), unsafe_allow_html=True)
        else:
            st.success("Great fit. The resume covers all detected JD skills.")
        st.markdown("</div>", unsafe_allow_html=True)

    with t2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("Skills by Bucket (Resume vs JD)")
        rows = []
        for bucket in skills_by_bucket.keys():
            rs = found_by_bucket_resume.get(bucket, [])
            js = found_by_bucket_jd.get(bucket, [])
            cov = len(set(rs).intersection(js))
            total = max(len(js), 1)
            coverage_pct = int((cov / total) * 100)
            rows.append(
                {
                    "Bucket": bucket,
                    "Resume skills": ", ".join(rs[:10]) if rs else "-",
                    "JD skills": ", ".join(js[:10]) if js else "-",
                    "Overlap count": cov,
                    "Coverage": coverage_pct,
                }
            )
        df = pd.DataFrame(rows).sort_values("Overlap count", ascending=False)
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("Bucket Coverage")
        for bucket in skills_by_bucket.keys():
            rs = found_by_bucket_resume.get(bucket, [])
            js = found_by_bucket_jd.get(bucket, [])
            total = max(len(js), 1)
            cov = len(set(rs).intersection(js))
            coverage_pct = int((cov / total) * 100)
            st.write(f"{bucket} - {coverage_pct}%")
            st.markdown(
                f"<div class='bucket-bar'><div class='bucket-fill' style='width: {coverage_pct}%'></div></div>",
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("Matched & Missing Skills")
        st.write("Matched")
        st.markdown(_chips(matched_skills), unsafe_allow_html=True)
        st.write("Missing")
        st.markdown(_chips(missing_skills, missing=True), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with t3:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("Job Description")
        st.text(jd_text)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("Resume Extracted Text")
        st.text(resume_text[:3000] + ("..." if len(resume_text) > 3000 else ""))
        st.caption("Preview is truncated to keep the interface readable.")
        st.markdown("</div>", unsafe_allow_html=True)

    with t4:
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
            "Download JSON Report",
            data=json.dumps(report, indent=2).encode("utf-8"),
            file_name="ats_report.json",
            mime="application/json",
            use_container_width=True,
        )

st.markdown("</div>", unsafe_allow_html=True)
