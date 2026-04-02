from django.urls import path
from .views import GenerateSummaryView, SummaryHistoryListView

urlpatterns = [
    path('generate/', GenerateSummaryView.as_view(), name='summary-generate'),
    path('history/', SummaryHistoryListView.as_view(), name='summary-history'),
]