from rest_framework import generics, status
from rest_framework.response import Response
from .models import Upload
from .serializers import UploadSerializer
from studyroom.models import StudySession
from django.shortcuts import get_object_or_404

class UploadCreateView(generics.CreateAPIView):
    serializer_class = UploadSerializer

    def create(self, request, *args, **kwargs):
        session_id = request.data.get('session')
        session = get_object_or_404(StudySession, id=session_id)

        # Attach session automatically
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(session=session)

        # Return response
        return Response({
            "id": serializer.instance.id,
            "file": serializer.instance.file.url,
            "file_type": serializer.instance.file_type,
            "message": "File uploaded successfully"
        }, status=status.HTTP_201_CREATED)