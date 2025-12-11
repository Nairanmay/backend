from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CompanyProfileViewSet

router = DefaultRouter()
router.register(r'', CompanyProfileViewSet, basename='company_profile')

urlpatterns = [
    path('', include(router.urls)),
]