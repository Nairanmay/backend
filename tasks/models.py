from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator


class Project(models.Model):
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=50, choices=[('individual', 'Individual'), ('group', 'Group')])
    deadline = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    # --- ADD THIS LINE ---
    company_code = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.name

class Task(models.Model):
    project = models.ForeignKey(Project, related_name='tasks', on_delete=models.CASCADE)
    description = models.TextField()
    
    # --- CHANGE THIS LINE: update related_name to 'assigned_tasks' ---
    assigned_to = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='assigned_tasks')
    
    status = models.CharField(max_length=20, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    requires_document = models.BooleanField(default=False)
    document = models.FileField(upload_to='task_documents/', null=True, blank=True)
    admin_checked = models.BooleanField(default=False)
    company_code = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.description
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
