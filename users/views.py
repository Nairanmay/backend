from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import CustomUser, Task, RefreshToken
from .serializers import RegisterSerializer, UserSerializer, TaskSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

# Registration View
class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print("Validation Errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# Get Current Logged-in User Info
class UserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


# Admin-only: View All Users in the Same Company
class CompanyUsersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, company_code):  # Accept company_code param
        user = request.user
        if user.role != "admin":
            return Response({"error": "Only admins can view company users."}, status=status.HTTP_403_FORBIDDEN)

        # Optionally, verify user.company_code matches company_code, or restrict as needed
        if user.company_code != company_code:
            return Response({"error": "You can only view users of your own company."}, status=status.HTTP_403_FORBIDDEN)

        users = CustomUser.objects.filter(company_code=company_code)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# Admin-only: Assign Task to a User in Same Company
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
        serializer = TaskSerializer(task)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# Get Tasks: Admin sees all company tasks, users see their own tasks
class TaskListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role == 'admin':
            tasks = Task.objects.filter(company_code=user.company_code)
        else:
            tasks = Task.objects.filter(assigned_to=user)
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# Custom Token Obtain Pair Serializer: store refresh token per user
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        refresh = data.get('refresh')

        # Save or update the refresh token for the user
        RefreshToken.objects.update_or_create(
            user=user,
            defaults={'token': refresh}
        )

        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
