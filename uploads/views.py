from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Upload
from .serializers import UploadSerializer
from studyroom.models import StudySession
from django.shortcuts import get_object_or_404
from .utils import extract_text_from_pdf
from ai_tutor.gemini_client import validate_subject_match
from rest_framework.exceptions import PermissionDenied
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
                return Response({
                    "error": validation.get('feedback', "Validation Failed"),
                    "detected_subject": validation.get('detected_subject'),
                    "detected_grade": validation.get('detected_grade')
                }, status=status.HTTP_400_BAD_REQUEST)
            
            upload.extracted_text = text
            upload.is_valid_for_subject = True
            upload.validation_feedback = validation.get('feedback')
            
            if upload.source_type == 'system':
                from ai_tutor.gemini_client import generate_textbook_map
                # This creates the searchable index
                book_map = generate_textbook_map(text)
                upload.table_of_contents = book_map
                # For system books, we can auto-activate them
                upload.is_active = True
            
            upload.save()
         

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class UploadListView(generics.ListAPIView):
    serializer_class = UploadSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        session_id = self.request.query_params.get('session_id')
        if not session_id:
            return Upload.objects.none()
        
        # Security: Only return uploads for sessions owned by the current user
        return Upload.objects.filter(
            session_id=session_id, 
            session__user=self.request.user
        ).order_by('created_at')

class UploadDeleteView(generics.DestroyAPIView):
    queryset = Upload.objects.all()
    serializer_class = UploadSerializer

    def perform_destroy(self, instance):
        # 1. Security Check: Is this a 'system' book?
        if instance.source_type == 'system':
            raise PermissionDenied("You cannot delete official system textbooks.")
        
        # 2. Security Check: Does this book belong to the current user?
        if instance.session.user != self.request.user:
            raise PermissionDenied("You do not have permission to delete this file.")

        # 3. Clean up the actual file from storage (UserPDF folder)
        if instance.file and os.path.exists(instance.file.path):
            os.remove(instance.file.path)
            
        # 4. Delete the database record
        instance.delete()

@api_view(['POST'])
def activate_upload(request, upload_id):
    """
    Activates a specific book (tab) and deactivates all others in the same session.
    """
    upload = get_object_or_404(Upload, id=upload_id, session__user=request.user)
    
    # 1. Deactivate all books in this specific study session
    Upload.objects.filter(session=upload.session).update(is_active=False)
    
    # 2. Activate the selected one
    upload.is_active = True
    upload.save()
    
    return Response({"message": f"'{upload.file.name}' is now the active study material."})