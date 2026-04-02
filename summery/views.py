from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from django.shortcuts import get_object_or_404
import json, re

from .models import Summary
from .serializers import SummarySerializer
from uploads.models import Upload
from studyroom.models import StudySession
from ai_tutor.models import ChatMessage
from quiz.utils import identify_current_topic  # Reusing your quiz logic!
from ai_tutor.gemini_client import generate_ai_response
from ai_tutor.prompts import build_summary_generation_prompt

class GenerateSummaryView(APIView):
    def post(self, request):
        session_id = request.data.get("session_id")
        session = get_object_or_404(StudySession, id=session_id, user=request.user)

        # 1. Identify Current Topic from Chat
        recent_messages = ChatMessage.objects.filter(session=session).order_by('-created_at')[:10]
        chat_list = list(reversed(recent_messages))
        current_topic = identify_current_topic(chat_list)

        # 2. Check if this summary already exists for this session
        existing_summary = Summary.objects.filter(session=session, topic_title=current_topic).first()
        if existing_summary:
            return Response({
                "message": "Retrieving saved summary.",
                "summary": SummarySerializer(existing_summary).data
            }, status=status.HTTP_200_OK)

        # 3. Find Active Book and Slice
        active_upload = Upload.objects.filter(session=session, is_active=True).first()
        if not active_upload:
            return Response({"error": "No active book found to summarize."}, status=status.HTTP_400_BAD_REQUEST)

        full_text = active_upload.extracted_text or ""
        start_idx = full_text.lower().find(current_topic.lower())
        if start_idx == -1: start_idx = 0
        text_slice = full_text[start_idx : start_idx + 15000] # Slightly larger slice for summaries

        # 4. Generate with Gemini
        prompt = build_summary_generation_prompt(
            current_topic=current_topic,
            text_slice=text_slice,
            grade=session.grade_level,
            subject=session.subject.name
        )
        
        raw_ai_data = generate_ai_response(prompt)
        
        try:
            # Clean and Parse JSON
            clean_json = re.sub(r'```json|```', '', raw_ai_data).strip()
            data = json.loads(clean_json)

            # 5. Save to Database
            new_summary = Summary.objects.create(
                session=session,
                upload=active_upload,
                topic_title=current_topic,
                content=data.get('summary_text', ''),
                key_terms=data.get('key_terms', [])
            )

            return Response({
                "message": "New summary generated.",
                "summary": SummarySerializer(new_summary).data
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": f"Failed to parse summary: {str(e)}"}, status=500)
        
class SummaryHistoryListView(generics.ListAPIView):
    serializer_class = SummarySerializer

    def get_queryset(self):
        session_id = self.request.query_params.get('session_id')
        return Summary.objects.filter(
            session_id=session_id, 
            session__user=self.request.user
        ).order_by('-created_at')