from rest_framework import serializers
import os
from .models import Upload

class UploadSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    class Meta:
        model = Upload
        fields = ['id', 'session','name', 'file', 'file_type','source_type','is_active', 'created_at']
        read_only_fields = ['id', 'created_at', 'file_type']

    def validate_file(self, value):
        # For MVP: allow only PDF
        if not value.name.endswith('.pdf'):
            raise serializers.ValidationError("Only PDF files are supported for now.")
        return value
    
    def get_name(self, obj):
        # Extracts 'Geography_Notes.pdf' from the file path
        return os.path.basename(obj.file.name)