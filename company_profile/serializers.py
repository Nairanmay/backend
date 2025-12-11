from rest_framework import serializers
from .models import CompanyProfile

class CompanyProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyProfile
        fields = '__all__'
        read_only_fields = ['company_code', 'updated_at']