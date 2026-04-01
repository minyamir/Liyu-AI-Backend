from django.urls import path
from .views import UploadCreateView

urlpatterns = [
    path('upload/', UploadCreateView.as_view(), name='upload-create'),
]