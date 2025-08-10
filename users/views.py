from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import CustomUser, Task
from .serializers import RegisterSerializer, UserSerializer, TaskSerializer


# ✅ Registration View
class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print("Validation Errors:", serializer.errors)  # Debug log
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# ✅ Get Current User Info
class UserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


# ✅ View All Users in the Same Company (Admin Only)
class CompanyUsersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role != "admin":
            return Response({"error": "Only admins can view company users."}, status=status.HTTP_403_FORBIDDEN)

        users = CustomUser.objects.filter(company_code=user.company_code)
        return Response(UserSerializer(users, many=True).data, status=status.HTTP_200_OK)


# ✅ Assign Task (Admin Only, Same Company)
class AssignTaskView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        if user.role != 'admin':
            return Response({"error": "Only admins can assign tasks."}, status=status.HTTP_403_FORBIDDEN)

        assigned_to_username = request.data.get('assigned_to')
        title = request.data.get('title')
        description = request.data.get('description')

        if not assigned_to_username or not title:
            return Response({"error": "Username and title are required."}, status=status.HTTP_400_BAD_REQUEST)

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


# ✅ Get Tasks (Admin = all company tasks, User = own tasks)
class TaskListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role == 'admin':
            tasks = Task.objects.filter(company_code=user.company_code)
        else:
            tasks = Task.objects.filter(assigned_to=user)
        return Response(TaskSerializer(tasks, many=True).data, status=status.HTTP_200_OK)
