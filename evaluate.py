"""Compare TF-IDF, embeddings and hybrid scoring on eval/pairs.csv."""
import pandas as pd
from sklearn.metrics import roc_auc_score

from screening.matcher import embedding_score, hybrid_score, tfidf_score

df = pd.read_csv("eval/pairs.csv")
read = lambda p: open(p, encoding="utf-8").read()
resumes = df.resume_path.map(read)
jds = df.jd_path.map(read)

for name, fn in [("TF-IDF", tfidf_score), ("Embeddings", embedding_score), ("Hybrid", hybrid_score)]:
    scores = [fn(r, j) for r, j in zip(resumes, jds)]
    print(name, "ROC-AUC:", round(roc_auc_score(df.label, scores), 3))
