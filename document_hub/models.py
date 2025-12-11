from django.db import models
from django.conf import settings
import os

class Document(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='company_documents/')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    company_code = models.CharField(max_length=12)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def file_size(self):
        try:
            return f"{self.file.size / (1024 * 1024):.2f} MB"
        except:
            return "Unknown"

    @property
    def file_type(self):
        name = self.file.name.lower()
        if name.endswith('.pdf'): return 'pdf'
        if name.endswith(('.png', '.jpg', '.jpeg', '.svg')): return 'img'
        if name.endswith(('.xls', '.xlsx', '.csv')): return 'xlsx'
        return 'file'