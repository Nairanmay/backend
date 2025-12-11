from django.db import models

class CompanyProfile(models.Model):
    company_code = models.CharField(max_length=12, unique=True)
    name = models.CharField(max_length=255)
    industry = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    founded_date = models.DateField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name