from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import CustomUser, Task
from .serializers import RegisterSerializer, UserSerializer, TaskSerializer
class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print("Validation Errors:", serializer.errors)  # ✅ Debug here
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

class AssignTaskView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        user = request.user
        if user.role != 'admin':
            return Response({"error": "Only admins can assign tasks."}, status=status.HTTP_403_FORBIDDEN)

        assigned_to_username = request.data.get('assigned_to')
        title = request.data.get('title')
        description = request.data.get('description')

        try:
            assigned_user = CustomUser.objects.get(username=assigned_to_username, company_code=user.company_code)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found in your company."}, status=status.HTTP_404_NOT_FOUND)

        task = Task.objects.create(
            title=title,
            description=description,
            assigned_to=assigned_user,
            created_by=user,
            company_code=user.company_code
        )
        return Response(TaskSerializer(task).data, status=status.HTTP_201_CREATED)

class TaskListView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        user = request.user
        if user.role == 'admin':
            tasks = Task.objects.filter(company_code=user.company_code)
        else:
            tasks = Task.objects.filter(assigned_to=user)
        return Response(TaskSerializer(tasks, many=True).data)
