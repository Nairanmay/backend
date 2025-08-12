from django.contrib import admin
from django.urls import path
from django.http import JsonResponse
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.urls import path, include
from users.views import (
    RegisterView,
    UserView,
    AssignTaskView,
    TaskListView,
    CompanyUsersView,  # <-- You'll create this in views.py
)
from users.views import CustomTokenObtainPairView
from users.views import DeleteUserView

from rest_framework_simplejwt.views import TokenRefreshView
def home(request):
    return JsonResponse({"message": "API is running"})

urlpatterns = [
    path('', home),
   path('admin/', admin.site.urls),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Auth
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='login'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/user/', UserView.as_view(), name='user'),

    # Tasks
    path('tasks/assign/', AssignTaskView.as_view(), name='assign-task'),
    path('tasks/', TaskListView.as_view(), name='task-list'),

    # Manage Users by Company Code
    path('users/company/<str:company_code>/', CompanyUsersView.as_view(), name='company_users'),
 path('users/delete/<int:user_id>/', DeleteUserView.as_view(), name='delete-user'),

 # Pitch Deck Upload

    path('api/pitchdeck/', include('pitchdeck.urls')),

    # Funding Suggestor
     path('api/funding/', include('funding_suggestor.urls')),
]
