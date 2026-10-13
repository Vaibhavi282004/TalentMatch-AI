import csv
from collections import Counter

from django.db.models import Avg, Count, Max

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .matcher import (embedding_score, extract_skills, extract_text_from_pdf,
                      get_model, skill_gap, tfidf_score)
from .models import Candidate, Screening

MAX_SIZE = 5 * 1024 * 1024
MAX_FILES = 20


def home(request):
    error = None
    if request.method == "POST":
        jd = request.POST.get("job_description", "").strip()
        title = request.POST.get("title", "").strip()[:120]
        use_emb = request.POST.get("use_embeddings") == "on"
        files = request.FILES.getlist("resumes")

        if not jd:
            error = "Please paste a job description."
        elif not files:
            error = "Please upload at least one PDF resume."
        elif len(files) > MAX_FILES:
            error = f"Please upload at most {MAX_FILES} resumes at a time."

        if not error:
            if use_emb and get_model() is None:
                use_emb = False  # model not installed or could not load
            screening = Screening.objects.create(
                title=title, job_description=jd, used_embeddings=use_emb)

            for f in files:
                cand = Candidate(screening=screening, filename=f.name)
                if not f.name.lower().endswith(".pdf") or f.size > MAX_SIZE:
                    cand.error = "Not a PDF, or larger than 5 MB"
                else:
                    try:
                        text = extract_text_from_pdf(f)
                    except Exception:
                        text = ""
                        cand.error = "Could not read this PDF"
                    if not text and not cand.error:
                        cand.error = "No text found (scanned PDF?)"
                    if text:
                        t = tfidf_score(text, jd)
                        e = embedding_score(text, jd) if use_emb else None
                        cand.tfidf = round(t * 100, 1)
                        cand.embedding = None if e is None else round(e * 100, 1)
                        cand.score = round((t if e is None else 0.5 * t + 0.5 * e) * 100, 1)
                        gap = skill_gap(text, jd)
                        cand.matched, cand.missing = gap["matched"], gap["missing"]
                cand.save()
            return redirect("results", pk=screening.pk)

    recent = Screening.objects.all()[:5]
    return render(request, "screening/home.html", {"error": error, "recent": recent})


def results(request, pk):
    screening = get_object_or_404(Screening, pk=pk)
    candidates = list(screening.candidates.all())
    ok = [c for c in candidates if not c.error]
    failed = [c for c in candidates if c.error]
    jd_skills = sorted(extract_skills(screening.job_description))
    return render(request, "screening/results.html", {
        "screening": screening, "ok": ok, "failed": failed, "jd_skills": jd_skills})


def history(request):
    return render(request, "screening/history.html", {"screenings": Screening.objects.all()})


def export_csv(request, pk):
    screening = get_object_or_404(Screening, pk=pk)
    resp = HttpResponse(content_type="text/csv")
    resp["Content-Disposition"] = f'attachment; filename="screening_{pk}.csv"'
    w = csv.writer(resp)
    w.writerow(["Rank", "Resume", "Score %", "TF-IDF %", "Embedding %", "Matched skills", "Missing skills", "Error"])
    ranked = [c for c in screening.candidates.all() if not c.error]
    failed = [c for c in screening.candidates.all() if c.error]
    for i, c in enumerate(ranked, 1):
        w.writerow([i, c.filename, c.score, c.tfidf, c.embedding if c.embedding is not None else "",
                    ", ".join(c.matched), ", ".join(c.missing), ""])
    for c in failed:
        w.writerow(["", c.filename, "", "", "", "", "", c.error])
    return resp


def delete_screening(request, pk):
    if request.method == "POST":
        get_object_or_404(Screening, pk=pk).delete()
    return redirect("history")


def _top(counter, n=6):
    items = counter.most_common(n)
    mx = items[0][1] if items else 1
    return [{"name": k, "n": v, "pct": round(v / mx * 100)} for k, v in items]


def dashboard(request):
    cands = Candidate.objects.filter(error="")
    agg = cands.aggregate(avg=Avg("score"), best=Max("score"), n=Count("id"))
    matched, missing = Counter(), Counter()
    for c in cands.order_by("-id")[:300]:
        matched.update(c.matched)
        missing.update(c.missing)

    high = cands.filter(score__gte=60).count()
    mid = cands.filter(score__gte=40, score__lt=60).count()
    low = cands.filter(score__lt=40).count()
    total = (high + mid + low) or 1
    dist = [
        {"label": "Strong match (60% and up)", "n": high, "pct": round(high / total * 100), "cls": "good"},
        {"label": "Partial match (40-59%)", "n": mid, "pct": round(mid / total * 100), "cls": "mid"},
        {"label": "Weak match (under 40%)", "n": low, "pct": round(low / total * 100), "cls": "low"},
    ]
    recent = Screening.objects.annotate(top=Max("candidates__score"), cnt=Count("candidates"))[:6]
    return render(request, "screening/dashboard.html", {
        "n_screenings": Screening.objects.count(),
        "n_resumes": agg["n"],
        "avg": None if agg["avg"] is None else round(agg["avg"], 1),
        "best": agg["best"],
        "top_matched": _top(matched), "top_missing": _top(missing),
        "dist": dist, "recent": recent,
    })
