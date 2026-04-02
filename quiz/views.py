from rest_framework.views import APIView
from rest_framework import status, generics
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Quiz
from .serializers import QuizSerializer
from uploads.models import Upload
from studyroom.models import StudySession
from ai_tutor.models import ChatMessage
from .utils import identify_current_topic
from ai_tutor.gemini_client import generate_ai_response
from ai_tutor.prompts import build_quiz_generation_prompt
import json, re

class GenerateContextualQuizView(APIView):
    def post(self, request):
        session_id = request.data.get("session_id")
        session = get_object_or_404(StudySession, id=session_id, user=request.user)

        # 1. Find the Active Book
        active_upload = Upload.objects.filter(session=session, is_active=True).first()
        if not active_upload:
            return Response({"error": "No active book selected in this session."}, status=400)

        # 2. Get Recent Chat History (Last 10 messages, ordered correctly)
        recent_messages = ChatMessage.objects.filter(session=session).order_by('-created_at')[:10]
        # Reverse them so they are in chronological order for the AI
        chat_list = list(reversed(recent_messages))
        
        current_topic = identify_current_topic(chat_list)

        # 3. Slice the Book Text
        full_text = active_upload.extracted_text or ""
        # Search for the topic in the text (case-insensitive)
        start_idx = full_text.lower().find(current_topic.lower())
        
        if start_idx == -1: 
            start_idx = 0 # Fallback to beginning if topic isn't found in text
            
        text_slice = full_text[start_idx : start_idx + 12000]

        # 4. Generate Quiz via Gemini
        quiz_prompt = build_quiz_generation_prompt(
            current_topic=current_topic,
            text_slice=text_slice,
            grade=session.grade_level,
            subject=session.subject.name
        )
        raw_ai_data = generate_ai_response(quiz_prompt)
        
        try:
            # Clean and Parse JSON
            clean_json = re.sub(r'```json|```', '', raw_ai_data).strip()
            questions = json.loads(clean_json)

            # 5. Save to History
            quiz = Quiz.objects.create(
                session=session,
                upload=active_upload,
                topic_title=current_topic,
                questions_data=questions
            )

            return Response({
                "quiz_id": quiz.id,
                "topic": current_topic,
                "questions": questions
            })
        except Exception as e:
            return Response({"error": f"JSON Parsing failed: {str(e)}"}, status=500)
        
class SubmitQuizResultView(APIView):
    """
    Finalizes a quiz by saving the student's score and marking it as completed.
    """
    def post(self, request):
        # We expect the Frontend to send the Quiz ID and the final integer score
        quiz_id = request.data.get("quiz_id")
        score = request.data.get("score")

        # 1. Validation
        if quiz_id is None or score is None:
            return Response(
                {"error": "Missing quiz_id or score in request."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # 2. Security: Find the quiz but ensure it belongs to the current user's session
        quiz = get_object_or_404(Quiz, id=quiz_id, session__user=request.user)

        # 3. Update the record
        quiz.score = score
        quiz.is_completed = True
        quiz.save()

        # 4. Success Response
        return Response({
            "message": "Progress saved successfully!",
            "topic": quiz.topic_title,
            "score_recorded": f"{quiz.score}/{quiz.total_questions}",
            "is_completed": quiz.is_completed
        }, status=status.HTTP_200_OK)
        

class QuizHistoryListView(generics.ListAPIView):
    """
    Returns all quizzes associated with a specific study session.
    """
    serializer_class = QuizSerializer

    def get_queryset(self):
        # We get the session_id from the URL (e.g., ?session_id=5)
        session_id = self.request.query_params.get('session_id')
        
        if not session_id:
            return Quiz.objects.none()
            
        # Security: Only show quizzes for sessions belonging to the logged-in user
        return Quiz.objects.filter(
            session_id=session_id, 
            session__user=self.request.user
        ).order_by('-created_at') # Newest quizzes first