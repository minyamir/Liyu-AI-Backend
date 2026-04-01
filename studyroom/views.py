from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from subjects.models import Subject
from .models import StudySession

class StartStudySessionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        subject_id = request.data.get("subject_id")

        # Validate subject
        try:
            subject = Subject.objects.get(id=subject_id)
        except Subject.DoesNotExist:
            return Response({"error": "Subject not found"}, status=404)

        # Create session
        session = StudySession.objects.create(
            user=user,
            subject=subject,
            grade_level=user.grade_level,
            language=user.preferred_language
        )

        return Response({
            "session_id": session.id,
            "subject": subject.name,
            "grade": session.grade_level,
            "language": session.language
        })