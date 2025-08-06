from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('user', 'User'),
    )

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    company_code = models.CharField(max_length=12, blank=True, null=True)

    def save(self, *args, **kwargs):
        # If role is admin and no company_code, generate one
        if self.role == 'admin' and not self.company_code:
            self.company_code = str(uuid.uuid4())[:8].upper()  # e.g., 'A1B2C3D4'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} ({self.role})"


class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    assigned_to = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="tasks")
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="created_tasks")
    company_code = models.CharField(max_length=12)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} -> {self.assigned_to.username}"
