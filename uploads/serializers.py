from rest_framework import serializers
from .models import Upload

class UploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Upload
        fields = ['id', 'session', 'file', 'file_type','source_type','is_active', 'created_at']
        read_only_fields = ['id', 'created_at', 'file_type']

    def validate_file(self, value):
        # For MVP: allow only PDF
        if not value.name.endswith('.pdf'):
            raise serializers.ValidationError("Only PDF files are supported for now.")
        return value