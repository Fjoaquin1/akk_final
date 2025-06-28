# AAK-Test/django_task_api/tasks/serializers.py

from rest_framework import serializers
from .models import Task, Label
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying basic user information (e.g., as owner of a task/label).
    It only includes the user's ID and username for read operations.
    """
    class Meta:
        model = User
        fields = ['id', 'username']

class LabelSerializer(serializers.ModelSerializer):
    """
    Serializer for the Label model.
    Handles serialization/deserialization of Label objects.
    """
    owner = UserSerializer(read_only=True)
    """
    Nested serializer to display the full user object (id, username) when reading a Label.
    It's `read_only` because the owner is set by the backend based on the authenticated user.
    """
    owner_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='owner', write_only=True, required=False
    )
    """
    A write-only field to accept the primary key (ID) of a User during creation or update.
    This allows setting the owner by ID in API requests, mainly useful for administrators.
    `source='owner'` maps this field to the 'owner' attribute of the Label model.
    `required=False` allows omitting this field if the owner is set automatically by the view.
    """

    class Meta:
        model = Label
        fields = ['id', 'name', 'owner', 'owner_id']
        read_only_fields = ['owner']
        """
        Specifies fields that should only be included in serialized output and
        are not used for deserialization (i.e., cannot be set by client input).
        'owner' is read-only because it's set implicitly by the authenticated user in the view.
        """
    
class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer for the Task model.
    Handles serialization/deserialization of Task objects, including related Labels.
    """
    owner = UserSerializer(read_only=True)
    """
    Nested serializer to display the full user object (id, username) when reading a Task.
    It's `read_only` as the owner is set by the backend.
    """
    owner_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='owner', write_only=True, required=False
    )
    """
    A write-only field to accept the primary key (ID) of a User for setting the task owner.
    Similar to LabelSerializer's owner_id, primarily for admin use or specific scenarios
    where the owner needs to be explicitly provided by ID in the request.
    """
    labels = LabelSerializer(many=True, read_only=True) 
    """
    Nested serializer to display the full details of associated Label objects when reading a Task.
    `many=True` indicates it's a many-to-many relationship (multiple labels).
    `read_only=True` means these details are for output only and cannot be set directly
    by client input; 'label_ids' is used for input instead.
    """
    label_ids = serializers.PrimaryKeyRelatedField( 
        many=True, queryset=Label.objects.all(), source='labels', write_only=True, required=False
    )
    """
    A write-only field to accept a list of primary keys (IDs) of Label objects when
    creating or updating a Task. This is the primary way clients associate labels with a task.
    `source='labels'` maps this field to the 'labels' ManyToManyField of the Task model.
    `required=False` allows creating/updating tasks without providing any labels.
    """

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'completion_status',
            'owner', 'owner_id', 'labels', 'label_ids',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'owner']
        """
        Specifies fields that are only for output and cannot be provided by the client.
        'created_at' and 'updated_at' are auto-generated timestamps.
        'owner' is read-only because it's set implicitly by the authenticated user in the view.
        """

# Renamed from UserSerializer for clarity, as this is for user registration/creation
class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for registering (creating) new User accounts.
    It includes fields for username, email, and password.
    The password field is `write_only` for security.
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}
        """
        `extra_kwargs` provides additional options for specific fields.
        `'password': {'write_only': True}` ensures the password is accepted on input
        but never serialized back into the API response for security.
        """

    def create(self, validated_data):
        """
        Overrides the default `create` method to handle password hashing.
        Instead of directly saving the password, it uses `create_user` which correctly hashes the password.
        """
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''), # Email is optional, uses an empty string if not provided
            password=validated_data['password']
        )
        return user