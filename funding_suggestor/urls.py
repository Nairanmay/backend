from django.urls import path
from .views import FundingSuggestionView

urlpatterns = [
    path('suggest/', FundingSuggestionView.as_view(), name='funding-suggest'),
]
