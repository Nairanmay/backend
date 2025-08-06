from rest_framework import serializers
from .models import CustomUser, Task


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    company_code = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'password', 'role', 'company_code']

    def validate(self, data):
        role = data.get('role', 'user')

        if role == 'user' and not data.get('company_code'):
            raise serializers.ValidationError({"company_code": "Company code is required for users."})

        return data

    def create(self, validated_data):
        company_code = validated_data.get('company_code', None)
        role = validated_data.get('role', 'user')

        # Create user
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role=role
        )

        # If user is admin, company_code will auto-generate in model's save()
        if role == 'admin':
            user.save()
        else:
            # If user, assign the provided company_code
            user.company_code = company_code
            user.save()

        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'role', 'company_code']


class TaskSerializer(serializers.ModelSerializer):
    assigned_to = serializers.CharField(source='assigned_to.username', read_only=True)
    created_by = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'assigned_to', 'created_by', 'company_code', 'created_at']
