from django.urls import path
from .views import *

urlpatterns = [
    path('upload/', UploadCreateView.as_view(), name='upload-create'),
    path('list/', UploadListView.as_view(), name='upload-list'),
    path('<int:upload_id>/activate/', activate_upload, name='upload-activate'),
    
    path('<int:pk>/delete/', UploadDeleteView.as_view(), name='upload-delete'),
]