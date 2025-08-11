from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class PitchDeckAnalysis(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='pitchdecks/')
    analysis_text = models.TextField(blank=True, null=True)
    ratings = models.JSONField(blank=True, null=True)  # e.g. {"clarity": 8, "design": 7}
    chart_data = models.JSONField(blank=True, null=True)  # e.g. for pie/bar charts
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"PitchDeck by {self.user.username} on {self.created_at}"
