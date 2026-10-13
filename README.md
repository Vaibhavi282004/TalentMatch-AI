# AI Resume Screening

Django web app that ranks PDF resumes against a job description.

## Features
- Upload up to 20 PDF resumes at once (drag and drop)
- Hybrid scoring: TF-IDF + sentence embeddings (all-MiniLM-L6-v2); embeddings can be switched off
- Ranked candidate list with score bars
- Skill-gap report: matched and missing skills per candidate
- Screening history, CSV export, delete
- Uploaded PDFs are read in memory and not stored

## Run locally (Windows)
    python -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt
    python manage.py makemigrations screening
    python manage.py migrate
    python manage.py runserver

Open http://127.0.0.1:8000/

## Evaluation
    python make_eval.py
    python evaluate.py

| Method | ROC-AUC (36-pair synthetic set) |
|---|---|
| TF-IDF | (add your number) |
| Embeddings | (add your number) |
| Hybrid | (add your number) |

The synthetic set is small and easy; treat the numbers as a sanity check, not a benchmark.

## Limitations
- The skills list is hand-made (see `screening/matcher.py`).
- Scanned (image-only) PDFs have no text and are reported as unreadable.
