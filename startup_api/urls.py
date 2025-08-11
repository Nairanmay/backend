from django.contrib import admin
from django.urls import path
from django.http import JsonResponse
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from users.views import (
    RegisterView,
    UserView,
    AssignTaskView,
    TaskListView,
    CompanyUsersView,  # <-- You'll create this in views.py
)

def home(request):
    return JsonResponse({"message": "API is running"})

urlpatterns = [
    path('', home),
    path('admin/', admin.site.urls),

    # Auth
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='login'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
   path('api/company-users/', CompanyUsersView.as_view(), name='company-users'),


    # Tasks
    path('tasks/assign/', AssignTaskView.as_view(), name='assign-task'),
    path('tasks/', TaskListView.as_view(), name='task-list'),

    # Manage Users by Company Code
    path('users/company/<str:company_code>/', CompanyUsersView.as_view(), name='company-users'),
]
