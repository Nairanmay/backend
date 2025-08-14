from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.core.mail import send_mail
from django.conf import settings

from .models import Project, Task
from .serializers import ProjectSerializer, TaskSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()  # <— important for delete
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(assigned_to=user)
    def perform_create(self, serializer):
        # Save task with assigned users
        task = serializer.save()
    #     # Send email notifications to assigned users
    #     emails = [user.email for user in task.assigned_to.all()]
    #     if emails:
    #         send_mail(
    #             subject=f"New Task Assigned: {task.project.name}",
    #             message=f"You have been assigned a new task: {task.description}",
    #             from_email=settings.DEFAULT_FROM_EMAIL,
    #             recipient_list=emails,
    #         )

    # def perform_update(self, serializer):
    #     task = serializer.save()
    #     # Notify admin if task is completed
    #     if task.status.lower() == "completed":
    #         send_mail(
    #             subject=f"Task Completed: {task.project.name}",
    #             message=f"The task '{task.description}' has been completed.",
    #             from_email=settings.DEFAULT_FROM_EMAIL,
    #             recipient_list=[settings.ADMIN_EMAIL],
    #         )
