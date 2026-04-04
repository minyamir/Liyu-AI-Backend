from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from uploads.models import Upload
from studyroom.models import StudySession
from .models import ChatMessage
from .gemini_client import generate_ai_response
from .prompts import build_tutor_prompt


class ChatView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # We use query_params because it's a GET request
        session_id = request.query_params.get("session_id")
        
        if not session_id:
            return Response({"error": "session_id is required"}, status=400)

        try:
            session = StudySession.objects.get(id=session_id, user=request.user)
        except StudySession.DoesNotExist:
            return Response({"error": "Session not found or unauthorized"}, status=404)

        # Fetch all messages for this session
        messages = ChatMessage.objects.filter(session=session).order_by('created_at')
        
        # Format the history for the frontend
        history = []
        for msg in messages:
            history.append({
                "id": msg.id,
                "sender": msg.sender, # "user" or "ai"
                "message": msg.message,
                "timestamp": msg.created_at
            })

        return Response(history)

    def post(self, request):
        session_id = request.data.get("session_id")
        user_message = request.data.get("message")

        # Validate session
        try:
            session = StudySession.objects.get(id=session_id, user=request.user)
        except StudySession.DoesNotExist:
            return Response({"error": "Invalid session Or Unauthorized."}, status=404)
        
        history_objs = ChatMessage.objects.filter(session=session).order_by('-created_at')[:6]
        is_first_message = (history_objs.count() == 0)
        
        chat_history_text = ""
        for msg in reversed(history_objs):
            role = "Student" if msg.sender == "user" else "Liyu AI"
            chat_history_text += f"{role}: {msg.message}\n"
            
        
        active_upload = Upload.objects.filter(session=session, is_active=True).first()
        context_from_book = ""
        
        if active_upload and active_upload.extracted_text:
            # --- NEW: Label the source so the AI knows what it's reading ---
            source_label = "OFFICIAL TEXTBOOK" if active_upload.source_type == 'system' else "USER NOTES"
            book_title = active_upload.file.name
            
            header = f"--- SOURCE: {source_label} ({book_title}) ---\n"
            
            if len(active_upload.extracted_text) < 10000:
                context_from_book = header + active_upload.extracted_text
            else:
                important_keywords = [w for w in user_message.split() if len(w) > 3]
                slice_text = ""
                for word in important_keywords:
                    index = active_upload.extracted_text.lower().find(word.lower())
                    if index != -1:
                        start = max(0, index - 1500)
                        end = min(len(active_upload.extracted_text), index + 3500)
                        slice_text = active_upload.extracted_text[start:end]
                        break
                
                if not slice_text:
                    slice_text = active_upload.extracted_text[:5000]
                
                # Combine header with the slice
                context_from_book = header + slice_text
        
        
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
            user_message=user_message,
            context_from_books=context_from_book,
            chat_history=chat_history_text,
            is_first_message=is_first_message
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