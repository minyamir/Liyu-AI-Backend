from django.urls import path
from .views import StartStudySessionView

urlpatterns = [
    path("start/", StartStudySessionView.as_view()),
]