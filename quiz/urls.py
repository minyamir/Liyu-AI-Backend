from django.urls import path
from .views import *

urlpatterns = [
    path('generate/', GenerateContextualQuizView.as_view(), name='quiz-generate'),
    path('submit-result/', SubmitQuizResultView.as_view(), name='quiz-submit-result'),
    path('history/', QuizHistoryListView.as_view(), name='quiz-history'),
]