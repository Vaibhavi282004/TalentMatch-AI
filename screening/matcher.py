"""Resume <-> job description matching. No Django imports, so it can be tested alone."""
import re

import pdfplumber
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

_model = None
_model_failed = False


def get_model():
    """Load the embedding model once. Returns None if it cannot be loaded."""
    global _model, _model_failed
    if _model is None and not _model_failed:
        try:
            from sentence_transformers import SentenceTransformer
            _model = SentenceTransformer("all-MiniLM-L6-v2")
        except Exception:
            _model_failed = True
    return _model


def extract_text_from_pdf(file):
    with pdfplumber.open(file) as pdf:
        return "\n".join((p.extract_text() or "") for p in pdf.pages).strip()


def tfidf_score(resume, jd):
    try:
        m = TfidfVectorizer(stop_words="english").fit_transform([resume, jd])
        return float(cosine_similarity(m[0], m[1])[0][0])
    except ValueError:
        return 0.0


def chunk_text(text, size=150):
    words = text.split()
    return [" ".join(words[i:i + size]) for i in range(0, len(words), size)] or [text]


def embedding_score(resume, jd):
    """Returns None when the embedding model is unavailable."""
    model = get_model()
    if model is None:
        return None
    from sentence_transformers import util
    r = model.encode(chunk_text(resume), convert_to_tensor=True)
    j = model.encode(chunk_text(jd), convert_to_tensor=True)
    sims = util.cos_sim(r, j)
    return max(0.0, float(sims.max(dim=1).values.mean()))


def hybrid_score(resume, jd, w=0.5):
    t = tfidf_score(resume, jd)
    e = embedding_score(resume, jd)
    return t if e is None else w * t + (1 - w) * e


# canonical skill -> accepted spellings
SKILLS = {
    "Python": ["python"], "Java": ["java"], "JavaScript": ["javascript", "js"],
    "TypeScript": ["typescript"], "C++": ["c++"], "SQL": ["sql"],
    "MySQL": ["mysql"], "PostgreSQL": ["postgresql", "postgres"], "MongoDB": ["mongodb"],
    "HTML": ["html", "html5"], "CSS": ["css", "css3"], "React": ["react", "reactjs", "react.js"],
    "Node.js": ["node.js", "nodejs"], "Django": ["django"], "Flask": ["flask"],
    "FastAPI": ["fastapi"], "Spring Boot": ["spring boot", "springboot"],
    "REST API": ["rest api", "rest apis", "restful"], "Git": ["git", "github"],
    "Docker": ["docker"], "Kubernetes": ["kubernetes", "k8s"], "AWS": ["aws"],
    "Azure": ["azure"], "GCP": ["gcp", "google cloud"], "Linux": ["linux"],
    "Machine Learning": ["machine learning", "ml"], "Deep Learning": ["deep learning"],
    "NLP": ["nlp", "natural language processing"], "Pandas": ["pandas"],
    "NumPy": ["numpy"], "scikit-learn": ["scikit-learn", "sklearn"],
    "TensorFlow": ["tensorflow"], "PyTorch": ["pytorch"], "Power BI": ["power bi", "powerbi"],
    "Tableau": ["tableau"], "Excel": ["excel", "ms excel"], "Streamlit": ["streamlit"],
    "Data Analysis": ["data analysis", "data analytics"], "Statistics": ["statistics"],
    "Matplotlib": ["matplotlib"], "OOP": ["oop", "object oriented", "object-oriented"],
    "DSA": ["dsa", "data structures", "algorithms"], "Agile": ["agile", "scrum"],
    "Selenium": ["selenium"], "Testing": ["testing", "qa"], "Jenkins": ["jenkins"],
    "CI/CD": ["ci/cd", "cicd"], "Communication": ["communication"],
}

_PATTERNS = {}
for _name, _aliases in SKILLS.items():
    _all = set(a.lower() for a in _aliases) | {_name.lower()}
    _PATTERNS[_name] = re.compile(
        r"(?<![\w+#.])(?:" + "|".join(re.escape(a) for a in sorted(_all, key=len, reverse=True)) + r")(?![\w+#])"
    )


def extract_skills(text):
    t = text.lower()
    return {name for name, pat in _PATTERNS.items() if pat.search(t)}


def skill_gap(resume, jd):
    r, j = extract_skills(resume), extract_skills(jd)
    return {"matched": sorted(r & j), "missing": sorted(j - r)}
