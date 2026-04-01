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
        session, created = StudySession.objects.get_or_create(
            user=user,
            subject=subject,
            grade_level=user.grade_level,
            defaults={"language": user.preferred_language},
            study_field = user.study_field,
        )

        return Response({
            "session_id": session.id,
            "subject": subject.name,
            "grade": session.grade_level,
            "feild":session.study_field,
            "language": session.language,
            "created": created
        })
 
class UpdateSessionLanguageView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        session_id = request.data.get("session_id")
        language = request.data.get("language")
        
        if language not in ["en", "am"]:
            return Response({"error": "Invalid language. Use 'en' or 'am'."}, status=400)

        try:
            session = StudySession.objects.get(id=session_id)
        except StudySession.DoesNotExist:
            return Response({"error": "Session not found"}, status=404)

        # security check
        if session.user != request.user:
            return Response({"error": "Unauthorized"}, status=403)

        # update session language
        session.language = language
        session.save()

        return Response({
            "message": "Language updated",
            "language": session.language
        })