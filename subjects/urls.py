from django.urls import path
from .views import *

urlpatterns = [
    path("", SubjectListView.as_view(), name="subjects"),
]