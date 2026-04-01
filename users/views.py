from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import *

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User created"}, status=201)

        return Response(serializer.errors, status=400)



class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        user = authenticate(request, username=email, password=password)

        if user is None:
            return Response({"error": "Invalid credentials"}, status=400)

        refresh = RefreshToken.for_user(user)

        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        })


from rest_framework.permissions import IsAuthenticated

class SetGradeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        grade = request.data.get("grade_level")

        request.user.grade_level = grade
        request.user.save()

        return Response({"message": "Grade saved"})
    

class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)