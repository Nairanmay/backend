from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.decorators import action
from rest_framework.response import Response
# from django.core.mail import send_mail
from django.conf import settings

from .models import Project, Task
from .serializers import ProjectSerializer, TaskSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    # Required for DRF router to generate URLs
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    # --- SECURITY FIX: Filter Projects by Company Code ---
    # This securely overrides the queryset above for actual users
    def get_queryset(self):
        user = self.request.user
        if getattr(user, 'company_code', None):
            return Project.objects.filter(company_code=user.company_code)
        return Project.objects.none()

    # --- FIX: Automatically save the admin's company code when creating a project ---
    def perform_create(self, serializer):
        serializer.save(company_code=self.request.user.company_code)

    def destroy(self, request, *args, **kwargs):
        project = self.get_object()
        incomplete_tasks = project.tasks.exclude(status__iexact="completed").count()
        if incomplete_tasks > 0:
            return Response(
                {"error": "Cannot delete project with incomplete tasks."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=["get"])
    def with_tasks(self, request):
        projects = self.get_queryset()
        data = []
        for project in projects:
            tasks = Task.objects.filter(project=project)
            data.append({
                "id": project.id,
                "name": project.name,
                "type": project.type,
                "deadline": project.deadline,
                "tasks": TaskSerializer(tasks, many=True).data
            })
        return Response(data)


class TaskViewSet(viewsets.ModelViewSet):
    # Required for DRF router to generate URLs
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (JSONParser, MultiPartParser, FormParser)

    # --- SECURITY FIX: Filter Tasks by Company Code ---
    def get_queryset(self):
        user = self.request.user
        if not getattr(user, 'company_code', None):
            return Task.objects.none()

        company_tasks = Task.objects.filter(project__company_code=user.company_code)

        if user.is_staff or getattr(user, 'role', '') == 'admin':
            return company_tasks
        return company_tasks.filter(assigned_to=user)

    # --- FIX: Automatically save the admin's company code when creating a task ---
    def perform_create(self, serializer):
        serializer.save(company_code=self.request.user.company_code)

    def perform_update(self, serializer):
        task = serializer.save()
        if task.status.lower() == "completed":
            pass  

    @action(detail=False, methods=["get"], permission_classes=[IsAdminUser])
    def uploaded_docs(self, request):
        tasks_with_docs = self.get_queryset().filter(document__isnull=False)
        serializer = self.get_serializer(tasks_with_docs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="upload-document")
    def upload_document(self, request, pk=None):
        task = self.get_object() 

        if not task.requires_document:
            return Response(
                {"error": "This task does not require a document."},
                status=status.HTTP_400_BAD_REQUEST
            )

        file = request.FILES.get("document")
        if not file:
            return Response(
                {"error": "No file uploaded."}, status=status.HTTP_400_BAD_REQUEST
            )

        task.document = file
        task.save()
        return Response({"message": "Document uploaded successfully."}, status=200)