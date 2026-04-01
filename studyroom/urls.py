from django.urls import path
from .views import *

urlpatterns = [
    path("start/", StartStudySessionView.as_view()),
    path("update-language/", UpdateSessionLanguageView.as_view()),
]