from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StakeholderViewSet, SecurityViewSet, IssuanceViewSet, CapTableSummaryView

router = DefaultRouter()
router.register(r'stakeholders', StakeholderViewSet, basename='stakeholder')
router.register(r'securities', SecurityViewSet, basename='security')
router.register(r'issuances', IssuanceViewSet, basename='issuance')

urlpatterns = [
    # This URL will return the final calculated cap table
    path('summary/', CapTableSummaryView.as_view(), name='cap-table-summary'),
    
    # These URLs are for adding/editing the raw data
    path('', include(router.urls)),
]