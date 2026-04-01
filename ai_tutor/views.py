from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from studyroom.models import StudySession
from .models import ChatMessage
from .gemini_client import generate_ai_response
from .prompts import build_tutor_prompt


class ChatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        session_id = request.data.get("session_id")
        user_message = request.data.get("message")

        # Validate session
        try:
            session = StudySession.objects.get(id=session_id, user=request.user)
        except StudySession.DoesNotExist:
            return Response({"error": "Invalid session Or Unauthorized."}, status=404)
 

        # Save user message
        ChatMessage.objects.create(
            session=session,
            sender="user",
            message=user_message
        )
        
        context = session.get_tutor_context()

        # Build smart prompt
        prompt = build_tutor_prompt(
            user_name=context['user_name'],
            subject=context['subject'],
            grade=context['grade'],
            field=context['field'],
            language=context['language'],
            user_message=user_message
        )

        # Get AI response
        ai_reply = generate_ai_response(prompt)

        # Save AI response
        ChatMessage.objects.create(
            session=session,
            sender="ai",
            message=ai_reply
        )

        return Response({
            "reply": ai_reply
        })