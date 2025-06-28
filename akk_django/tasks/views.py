# AAK-Test/django_task_api/tasks/views.py

from rest_framework import viewsets, permissions, status, generics
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Task, Label
from .serializers import TaskSerializer, LabelSerializer, UserRegistrationSerializer # Using UserRegistrationSerializer

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit or delete it.
    Read-only permissions (GET, HEAD, OPTIONS) are allowed for any authenticated user.
    """
    def has_object_permission(self, request, view, obj):
        """
        Check if the user has permission to perform an action on the object.
        """
        # Read permissions are allowed to any authenticated request.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner of the object.
        return obj.owner == request.user
    
class TaskViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for viewing and editing Task instances.
    Provides standard CRUD operations for Task objects.
    """
    queryset = Task.objects.all() 
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    """
    `permission_classes`: Specifies the permissions required to access Task endpoints.
    - `IsAuthenticated`: Ensures only authenticated users can access.
    - `IsOwnerOrReadOnly`: Ensures users can only perform write operations (create, update, delete)
      on tasks they own, while allowing read access to all tasks they are authorized to see.
    """

    def get_queryset(self):
        """
        Retrieves the queryset of tasks.
        If the requesting user is a staff member, all tasks are returned.
        Otherwise, only tasks owned by the requesting user are returned.
        """
        if self.request.user.is_staff:
            return Task.objects.all()
        return Task.objects.filter(owner=self.request.user)
    
    
    def perform_create(self, serializer):
        """
        Assigns the owner of a new task to the currently authenticated user.
        Also handles the association of labels, ensuring that only valid and
        user-owned labels can be linked to the task.
        """
        # Get the list of label IDs from the request data.
        labels_ids = self.request.data.get('label_ids', []) 
        
        # Ensure labels_ids is a list; if not, treat it as an empty list.
        labels_ids = labels_ids if isinstance(labels_ids, list) else [] 
        
        # Filter for labels that exist and are owned by the current user.
        valid_labels = Label.objects.filter(id__in=labels_ids, owner=self.request.user)
        
        # Validate that all provided label IDs correspond to existing and owned labels.
        if len(valid_labels) != len(labels_ids):
            raise ValidationError(
                {"label_ids": "One or more labels not found or do not belong to the authenticated user."}
            )
        
        # Save the task, setting the owner to the current user and associating the valid labels.
        serializer.save(owner=self.request.user, labels=valid_labels)


    def perform_update(self, serializer):
        """
        Handles updating a task instance.
        Prevents non-staff users from changing the owner of a task.
        Updates associated labels if `label_ids` are provided in the request.
        """
        # Prevent non-staff users from changing the owner of a task.
        # This check is crucial for security.
        if 'owner_id' in self.request.data and serializer.instance.owner != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied("You do not have permission to change the owner of this task.")
        
        # Get the 'label_ids' from the request data. Use .get() without default to check if it was sent.
        labels_ids = self.request.data.get('label_ids') 
        
        # If 'label_ids' is present in the request (even if empty), process the labels.
        if labels_ids is not None:
            # Ensure labels_ids is a list.
            if not isinstance(labels_ids, list):
                raise ValidationError({"label_ids": "The format for label_ids must be a list."})

            # Filter for labels that exist and are owned by the current user.
            valid_labels = Label.objects.filter(id__in=labels_ids, owner=self.request.user)
            
            # Validate that all provided label IDs are valid and owned by the user.
            if len(valid_labels) != len(labels_ids):
                raise ValidationError(
                    {"label_ids": "One or more labels not found or do not belong to the authenticated user."}
                )
            
            # Save the task with the updated labels.
            serializer.save(labels=valid_labels)
        else:
            # If 'label_ids' was not provided in the request, save without modifying labels.
            serializer.save()


class LabelViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for viewing and editing Label instances.
    Provides standard CRUD operations for Label objects.
    """
    queryset = Label.objects.all()
    serializer_class = LabelSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    """
    `permission_classes`: Specifies the permissions required to access Label endpoints.
    - `IsAuthenticated`: Ensures only authenticated users can access.
    - `IsOwnerOrReadOnly`: Ensures users can only perform write operations (create, update, delete)
      on labels they own, while allowing read access to all labels they are authorized to see.
    """

    def get_queryset(self):
        """
        Retrieves the queryset of labels.
        If the requesting user is a staff member, all labels are returned.
        Otherwise, only labels owned by the requesting user are returned.
        """
        if self.request.user.is_staff:
                return Label.objects.all()
        return Label.objects.filter(owner=self.request.user)
    
    def perform_create(self, serializer):
        """
        Assigns the owner of a new label to the currently authenticated user.
        Validates that the label name is unique for that specific user.
        """
        name = serializer.validated_data.get('name')
        # Check if a label with the same name already exists for the current user.
        if Label.objects.filter(name=name, owner=self.request.user).exists():
            raise ValidationError({'name': 'A label with this name already exists for this user.'}, code='unique')
        serializer.save(owner=self.request.user)


    def perform_update(self, serializer):
        """
        Handles updating a label instance.
        Prevents non-staff users from changing the owner of a label.
        Validates that the updated label name remains unique for the user.
        """
        # Prevent non-staff users from changing the owner of a label.
        if 'owner_id' in self.request.data and serializer.instance.owner != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied("You do not have permission to change the owner of this label.")

        name = serializer.validated_data.get('name')
        # If a new name is provided and it's different from the current one, validate uniqueness.
        if name and name != serializer.instance.name:
            if Label.objects.filter(name=name, owner=self.request.user).exclude(id=serializer.instance.id).exists():
                raise ValidationError({'name': 'A label with this name already exists for this user.'}, code='unique')
        serializer.save()


class UserRegistrationView(generics.CreateAPIView):
    """
    API view for user registration. Allows new users to create an account.
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer # Using the specific registration serializer
    permission_classes = [permissions.AllowAny] # Allows unauthenticated users to access this endpoint