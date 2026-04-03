from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import *

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("login/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("set-grade/", SetGradeView.as_view(), name="add-grade"),
    path("me/", ProfileView.as_view(), name="profiel"),
    
    path("set-field/", SetFieldView.as_view(), name="set-field"),
]