from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from .models import Project, Task
from .serializers import ProjectSerializer, TaskSerializer
from rest_framework.permissions import IsAuthenticated
from django.core.mail import send_mail
from django.conf import settings

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        task = serializer.save()
        # Email notification to assigned employees
        emails = [user.email for user in task.assigned_to.all()]
        send_mail(
            subject=f"New Task Assigned: {task.project.name}",
            message=f"You have been assigned a new task: {task.description}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=emails
        )

    def perform_update(self, serializer):
        task = serializer.save()
        if task.status.lower() == "completed":
            # Notify admin
            send_mail(
                subject=f"Task Completed: {task.project.name}",
                message=f"The task '{task.description}' has been completed.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.ADMIN_EMAIL]
            )
