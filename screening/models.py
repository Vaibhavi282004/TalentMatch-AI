from django.db import models


class Screening(models.Model):
    title = models.CharField(max_length=120, blank=True)
    job_description = models.TextField()
    used_embeddings = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title or f"Screening #{self.pk}"


class Candidate(models.Model):
    screening = models.ForeignKey(Screening, on_delete=models.CASCADE, related_name="candidates")
    filename = models.CharField(max_length=255)
    score = models.FloatField(default=0)
    tfidf = models.FloatField(default=0)
    embedding = models.FloatField(null=True, blank=True)
    matched = models.JSONField(default=list, blank=True)
    missing = models.JSONField(default=list, blank=True)
    error = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-score"]

    def __str__(self):
        return self.filename
