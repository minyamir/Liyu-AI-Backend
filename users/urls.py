from django.urls import path
from .views import *

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("set-grade/", SetGradeView.as_view(), name="add-grade"),
    path("me/", ProfileView.as_view(), name="profiel"),
]