
import re
import io
import yaml
import yake
from typing import List, Dict, Tuple
from pdfminer.high_level import extract_text as pdf_extract_text
from docx import Document
from sentence_transformers import SentenceTransformer, util
from rapidfuzz import fuzz

_SBERT_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

def _clean_text(t: str) -> str:
    if not t:
        return ""
    t = re.sub(r"\s+", " ", t)
    return t.strip()

def read_pdf(file_bytes: bytes) -> str:
    with io.BytesIO(file_bytes) as f:
        return _clean_text(pdf_extract_text(f))

def read_docx(file_bytes: bytes) -> str:
    with io.BytesIO(file_bytes) as f:
        doc = Document(f)
    return _clean_text("\n".join([p.text for p in doc.paragraphs]))

def load_skills(skills_yaml_text: str) -> Dict[str, List[str]]:
    data = yaml.safe_load(skills_yaml_text)
    for k, v in data.items():
        data[k] = list(dict.fromkeys([s.lower() for s in v]))
    return data

def keyword_extract(text: str, max_k: int = 20) -> List[str]:
    kw = yake.KeywordExtractor(top=max_k, stopwords=None)
    candidates = kw.extract_keywords(text)
    return [k for k, s in sorted(candidates, key=lambda x: x[1])]

def match_skills(text: str, skills_by_bucket: Dict[str, List[str]], fuzzy: bool = True) -> Tuple[Dict[str, List[str]], List[str]]:
    text_l = text.lower()
    found_by_bucket = {b: [] for b in skills_by_bucket.keys()}
    flat_skills = set()

    for bucket, skills in skills_by_bucket.items():
        for s in skills:
            present = False
            if s in text_l:
                present = True
            elif fuzzy:
                if any(fuzz.partial_ratio(s, chunk) >= 90 for chunk in text_l.split()):
                    present = True
            if present:
                found_by_bucket[bucket].append(s)
                flat_skills.add(s)

    for b in found_by_bucket:
        found_by_bucket[b] = sorted(list(dict.fromkeys(found_by_bucket[b])))
    return found_by_bucket, sorted(list(flat_skills))

class SbertScorer:
    def __init__(self):
        self.model = SentenceTransformer(_SBERT_MODEL_NAME)

    def score(self, resume_text: str, jd_text: str) -> float:
        if not resume_text or not jd_text:
            return 0.0
        emb_r = self.model.encode([resume_text], normalize_embeddings=True)
        emb_j = self.model.encode([jd_text], normalize_embeddings=True)
        sim = float(util.cos_sim(emb_r, emb_j)[0][0])
        score = max(0.0, min(100.0, (sim + 1) * 50.0))
        return round(score, 2)
