from rest_framework import serializers
from .models import Stakeholder, Security, Issuance

class StakeholderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stakeholder
        fields = ['id', 'company_code', 'name', 'stakeholder_type']
        # The company_code is set automatically by the view, so it should not be sent by the client.
        read_only_fields = ['company_code']

class SecuritySerializer(serializers.ModelSerializer):
    class Meta:
        model = Security
        fields = ['id', 'company_code', 'name', 'authorized_shares']
        read_only_fields = ['company_code']

class IssuanceSerializer(serializers.ModelSerializer):
    # To provide more context on the frontend without extra API calls
    stakeholder_name = serializers.CharField(source='stakeholder.name', read_only=True)
    security_name = serializers.CharField(source='security.name', read_only=True)

    class Meta:
        model = Issuance
        fields = [
            'id', 'company_code', 'stakeholder', 'security', 
            'date_issued', 'number_of_shares', 
            'stakeholder_name', 'security_name'
        ]
        read_only_fields = ['company_code', 'stakeholder_name', 'security_name']

