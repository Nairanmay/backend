from rest_framework import serializers
from .models import Document

class DocumentSerializer(serializers.ModelSerializer):
    uploaded_by_username = serializers.CharField(source='uploaded_by.username', read_only=True)
    file_size = serializers.ReadOnlyField()
    file_type = serializers.ReadOnlyField()
    date = serializers.DateTimeField(source='uploaded_at', format="%Y-%m-%d", read_only=True)

    class Meta:
        model = Document
        fields = ['id', 'title', 'description', 'file', 'uploaded_by_username', 'file_size', 'file_type', 'date']
        read_only_fields = ['uploaded_by', 'company_code']