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
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

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
        projects = Project.objects.all()
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
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (JSONParser, MultiPartParser, FormParser)

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Task.objects.all()
        return Task.objects.filter(assigned_to=user)

    def perform_create(self, serializer):
        task = serializer.save()
        # emails = [u.email for u in task.assigned_to.all() if u.email]
        # if emails:
        #     send_mail(
        #         subject=f"New Task Assigned: {task.project.name}",
        #         message=f"You have been assigned a new task: {task.description}",
        #         from_email=settings.DEFAULT_FROM_EMAIL,
        #         recipient_list=emails,
        #         fail_silently=True,
        #     )

    def perform_update(self, serializer):
        task = serializer.save()

        # Notify admin if completed
        if task.status.lower() == "completed":
            # send_mail(
            #     subject=f"Task Completed: {task.project.name}",
            #     message=f"The task '{task.description}' has been completed.",
            #     from_email=settings.DEFAULT_FROM_EMAIL,
            #     recipient_list=[settings.ADMIN_EMAIL],
            #     fail_silently=True,
            # )

            pass  # Email notifications commented out

    # Admin view of all uploaded documents
    @action(detail=False, methods=["get"], permission_classes=[IsAdminUser])
    def uploaded_docs(self, request):
        tasks_with_docs = Task.objects.filter(document__isnull=False)
        serializer = self.get_serializer(tasks_with_docs, many=True)
        return Response(serializer.data)

    # Manual document upload
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
