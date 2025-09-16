from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StakeholderViewSet, SecurityViewSet, IssuanceViewSet, CapTableSummaryView

# This router handles the creation, updating, and deletion of your cap table data.
router = DefaultRouter()
router.register(r'stakeholders', StakeholderViewSet, basename='stakeholder')
router.register(r'securities', SecurityViewSet, basename='security')
router.register(r'issuances', IssuanceViewSet, basename='issuance')

urlpatterns = [
    # This is the primary endpoint for your frontend to display the final table.
    path('summary/', CapTableSummaryView.as_view(), name='cap-table-summary'),
    
    # These endpoints allow admins to manage the raw data via the API.
    path('', include(router.urls)),
]

