from django.db import models
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Subject
from .serializers import SubjectSerializer

class SubjectListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # IMPORTANT: check if grade is set
        if not user.grade_level:
            return Response(
                {"error": "Please select your grade first"},
                status=400
            )
        
        is_high_school = user.grade_level in ["11", "12"]

        if not is_high_school:
            subjects = Subject.objects.filter(grade_level=user.grade_level)
        else:
            # grade 11 or 12 → show common subjects + user's field
            user_field = getattr(user, 'study_field', None) 
            
            subjects = Subject.objects.filter(grade_level=user.grade_level).filter(
                models.Q(field__isnull=True) | models.Q(field=user_field)
            )

        serializer = SubjectSerializer(subjects, many=True)
        return Response(serializer.data)