from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings

from .models import Project, Task
from .serializers import ProjectSerializer, TaskSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)  # ✅ enable file upload

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            # Admin sees all tasks
            return Task.objects.all()
        # Employees see only tasks assigned to them
        return Task.objects.filter(assigned_to=user)

    def perform_create(self, serializer):
        task = serializer.save()

        # Optional email notification to assigned users
        emails = [user.email for user in task.assigned_to.all() if user.email]
        if emails:
            send_mail(
                subject=f"New Task Assigned: {task.project.name}",
                message=f"You have been assigned a new task: {task.description}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=emails,
                fail_silently=True,
            )

    def perform_update(self, serializer):
        task = serializer.save()

        # Restrict doc upload if not required
        if task.document and not task.requires_document:
            task.document.delete(save=False)  # remove invalid upload
            raise ValueError("This task does not require a document upload.")

        # Optional: send notification when task is marked completed
        if task.status.lower() == "completed":
            send_mail(
                subject=f"Task Completed: {task.project.name}",
                message=f"The task '{task.description}' has been completed.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.ADMIN_EMAIL],
                fail_silently=True,
            )

    # ✅ Admin view of all uploaded documents
    @action(detail=False, methods=["get"], permission_classes=[IsAdminUser])
    def uploaded_docs(self, request):
        tasks_with_docs = Task.objects.filter(document__isnull=False)
        serializer = self.get_serializer(tasks_with_docs, many=True)
        return Response(serializer.data)

    # ✅ New endpoint: upload document for a specific task
    @action(detail=True, methods=["post"], url_path="upload")
    def upload_document(self, request, pk=None):
        task = self.get_object()

        if not task.requires_document:
            return Response(
                {"error": "This task does not require a document."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        file = request.FILES.get("document")
        if not file:
            return Response(
                {"error": "No file uploaded."}, status=status.HTTP_400_BAD_REQUEST
            )

        task.document = file
        task.save()
        return Response({"message": "File uploaded successfully."}, status=200)
