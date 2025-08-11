from django.urls import path
from .views import PitchDeckAnalysisView

urlpatterns = [
    path('analyze/', PitchDeckAnalysisView.as_view(), name='pitchdeck-analyze'),
]
