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

        subjects = Subject.objects.filter(grade_level=user.grade_level)

        serializer = SubjectSerializer(subjects, many=True)
        return Response(serializer.data)