from rest_framework import serializers
from .models import Stakeholder, Security, Issuance

class StakeholderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stakeholder
        fields = '__all__'

class SecuritySerializer(serializers.ModelSerializer):
    class Meta:
        model = Security
        fields = '__all__'

class IssuanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issuance
        fields = '__all__'