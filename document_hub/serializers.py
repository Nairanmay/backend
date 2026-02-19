from rest_framework import serializers
from .models import Document # (Or whatever your model is named)

class DocumentSerializer(serializers.ModelSerializer):
    # 1. Add this custom field
    file_size = serializers.SerializerMethodField()

    class Meta:
        model = Document
        # 2. Make sure 'file_size' is included in your fields list
        fields = ['id', 'title', 'description', 'file', 'file_size', 'uploaded_by', 'created_at'] 

    # 3. Add this method to calculate the size in bytes
    def get_file_size(self, obj):
        try:
            if obj.file and hasattr(obj.file, 'size'):
                return obj.file.size
        except Exception:
            pass
        return 0