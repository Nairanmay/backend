from rest_framework import serializers
from .models import Project, Task
from django.contrib.auth import get_user_model
from users.models import CustomUser
User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        # Make sure 'company_code' is included here
        fields = ['id', 'name', 'type', 'deadline', 'created_at', 'company_code', 'tasks'] 
        read_only_fields = ['company_code'] # Add this so the backend handles it securely

class TaskSerializer(serializers.ModelSerializer):
    # This will output the full user objects when READING data (GET)
    assigned_to = UserSerializer(many=True, read_only=True)
    
    # This allows us to accept a list of IDs when WRITING data (POST/PUT)
    assigned_to_ids = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=CustomUser.objects.all(), 
        source='assigned_to', 
        write_only=True
    )
    
    # Same trick for project, so we get the full project details on GET, but can pass an ID on POST
    project_details = serializers.SerializerMethodField()

    class Meta:
        model = Task
        # Make sure assigned_to_ids is in the fields list
        fields = ['id', 'project', 'project_details', 'description', 'assigned_to', 'assigned_to_ids', 'status', 'created_at', 'requires_document', 'document', 'admin_checked', 'company_code']
        read_only_fields = ['company_code']

    def get_project_details(self, obj):
        return {
            "id": obj.project.id,
            "name": obj.project.name,
            "type": obj.project.type,
            "deadline": obj.project.deadline
        }

class ProjectSerializer(serializers.ModelSerializer):
    # This will embed all the tasks inside the project payload
    tasks = TaskSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = ['id', 'name', 'type', 'deadline', 'created_at', 'company_code', 'tasks']
        read_only_fields = ['company_code']