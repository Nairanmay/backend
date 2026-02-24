from rest_framework import serializers
from .models import Document # (Or whatever your model is named)

class DocumentSerializer(serializers.ModelSerializer):
    uploaded_by_username = serializers.CharField(source='uploaded_by.username', read_only=True)
    # --- ADD THIS: Tells Django to calculate the file size ---
    file_size = serializers.SerializerMethodField()

    class Meta:
        model = Document
        # --- ADD 'file_size' TO THIS LIST ---
        fields = ['id', 'title', 'description', 'file', 'file_size', 'uploaded_by', 'uploaded_by_username', 'uploaded_at']
        read_only_fields = ['uploaded_by', 'uploaded_at']

    # --- ADD THIS FUNCTION: Grabs the size in bytes directly from the file ---
    def get_file_size(self, obj):
        try:
            if obj.file and hasattr(obj.file, 'size'):
                return obj.file.size
        except Exception:
            pass
        return 0