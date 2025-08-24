from rest_framework import serializers
from .models import Project, Task
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name', 'type', 'deadline']


class TaskSerializer(serializers.ModelSerializer):
    assigned_to = UserSerializer(many=True, read_only=True)
    assigned_to_ids = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), many=True, write_only=True
    )

    # ✅ Include project details instead of just ID
    project = ProjectSerializer(read_only=True)
    project_id = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(), write_only=True, source="project"
    )

    # ✅ Document field
    document = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = Task
        fields = [
            'id',
            'project',           # detailed project object (read-only)
            'project_id',        # for writing (assigning project)
            'description',
            'assigned_to',
            'assigned_to_ids',
            'status',
            'created_at',
            'requires_document',  # ✅ new field
            'document',
            'admin_checked',      # ✅ new field
        ]

    def create(self, validated_data):
        assigned_users = validated_data.pop('assigned_to_ids', [])
        task = Task.objects.create(**validated_data)
        task.assigned_to.set(assigned_users)
        return task

    def update(self, instance, validated_data):
        assigned_users = validated_data.pop('assigned_to_ids', None)
        if assigned_users is not None:
            instance.assigned_to.set(assigned_users)
        return super().update(instance, validated_data)
