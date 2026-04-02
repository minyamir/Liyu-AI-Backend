from rest_framework import generics, status
from rest_framework.response import Response
from .models import Upload
from .serializers import UploadSerializer
from studyroom.models import StudySession
from django.shortcuts import get_object_or_404
from .utils import extract_text_from_pdf
from ai_tutor.gemini_client import validate_subject_match
import os

class UploadCreateView(generics.CreateAPIView):
    serializer_class = UploadSerializer

    def create(self, request, *args, **kwargs):
        session_id = request.data.get('session')
        session = get_object_or_404(StudySession, id=session_id, user=request.user)

        # Attach session automatically
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        upload = serializer.save(session=session)
        
        if upload.file_type == 'pdf':
            text = extract_text_from_pdf(upload.file)
            
            validation = validate_subject_match(text, session.subject.name, session.grade_level, session.language)
            
            if not validation['is_match']:
                # The user uploaded the wrong subject!
                file_path = upload.file.path
                if os.path.exists(file_path):
                    os.remove(file_path)
                
                upload.delete()
                error_msg = (
                    f"Validation Failed! Liyu AI detected this as {validation.get('detected_subject')} "
                    f"for {validation.get('detected_grade')}. "
                    f"This room is for {session.subject.name} Grade {session.grade_level}."
                ) 
                return Response({"error": error_msg}, status=status.HTTP_400_BAD_REQUEST)
            
            upload.extracted_text = text
            upload.is_valid_for_subject = True
            upload.validation_feedback = validation.get('feedback')
            upload.save()
         

        return Response(serializer.data, status=status.HTTP_201_CREATED)