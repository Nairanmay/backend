from rest_framework import serializers
from .models import Project, Task
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class TaskSerializer(serializers.ModelSerializer):
    assigned_to = UserSerializer(many=True, read_only=True)
    assigned_to_ids = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), many=True, write_only=True
    )

    class Meta:
        model = Task
        fields = ['id', 'project', 'description', 'assigned_to', 'assigned_to_ids', 'status', 'created_at']

    def create(self, validated_data):
        assigned_users = validated_data.pop('assigned_to_ids', [])
        task = Task.objects.create(**validated_data)
        task.assigned_to.set(assigned_users)
        return task

class ProjectSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = ['id', 'name', 'type', 'deadline', 'tasks']
