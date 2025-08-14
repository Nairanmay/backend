from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings

class Project(models.Model):
    PROJECT_TYPES = [
        ('individual', 'Individual'),
        ('group', 'Group'),
    ]
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=PROJECT_TYPES)
    deadline = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Task(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tasks")
    description = models.TextField()
    assigned_to = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="assigned_tasks")
    status = models.CharField(max_length=20, default="Pending")  # Pending, Completed
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.project.name} - {self.description[:20]}"
