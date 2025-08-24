from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator


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

    # ✅ Admin sets if document is required

   
    
    document = models.FileField(upload_to="task_docs/", null=True, blank=True)
    admin_checked = models.BooleanField(default=False)
    requires_document = models.BooleanField(default=False)

    # ✅ Employee uploads one document (if required)
    document = models.FileField(
        upload_to="task_documents/",
        blank=True,
        null=True,
        validators=[FileExtensionValidator(
            allowed_extensions=['pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx']
        )],
        help_text="Upload a document (PDF, Word, PPT, Excel)"
    )

    # ✅ Admin approval checkbox
    admin_checked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.project.name} - {self.description[:20]}"
