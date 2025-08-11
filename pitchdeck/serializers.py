from rest_framework import serializers
from .models import PitchDeckAnalysis

class PitchDeckAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = PitchDeckAnalysis
        fields = '__all__'
        read_only_fields = ['user', 'analysis_text', 'ratings', 'chart_data', 'created_at']
class PitchDeckUploadSerializer(serializers.Serializer):
    file = serializers.FileField()