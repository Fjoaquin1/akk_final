# AAK-Test/django_task_api/tasks/models.py

from django.db import models
from django.conf import settings # Import settings to reference AUTH_USER_MODEL

class Label(models.Model):
    """
    Represents a category or tag that can be associated with tasks.
    Each label belongs to a specific user.
    """
    name = models.CharField(max_length=100)
    """
    The name of the label (e.g., "Work", "Personal", "Urgent").
    Maximum length is 100 characters.
    """
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, # References the default User model configured in Django settings.
        on_delete=models.CASCADE, # If the owner user is deleted, all their labels will also be deleted.
        related_name='labels' # Allows accessing all labels for a user via `user.labels.all()`.
    )
    """
    A foreign key relationship to the User model.
    This field indicates which user owns this specific label, ensuring data isolation.
    """

    class Meta:
        unique_together = ('name', 'owner',)
        """
        Defines a unique constraint across multiple fields.
        This ensures that a single user cannot have two labels with the exact same name.
        For example, User A cannot have two labels named "Work", but User B can have one named "Work".
        """

    def __str__(self):
        """
        String representation of the Label object.
        Returns the name of the label, which is useful for display in the Django admin and debugging.
        """
        return self.name
    

class Task(models.Model):
    """
    Represents a single task item.
    Each task belongs to a specific user and can have multiple labels.
    """
    STATUS_CHOICE = [
        ('TODO', 'To Do'),
        ('IN_PROGRESS', 'IN Progress'),
        ('DONE', 'Done'),
    ]
    """
    Defines the available choices for the `completion_status` field.
    Each tuple contains the database value (e.g., 'TODO') and the human-readable display name (e.g., 'To Do').
    """
    title = models.CharField(max_length=200)
    """
    The main title or short description of the task.
    Maximum length is 200 characters.
    """
    description = models.TextField(blank=True, null=True)
    """
    A longer, optional description of the task.
    `blank=True` allows the field to be empty in forms.
    `null=True` allows the database field to store NULL values for empty descriptions.
    """
    completion_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICE, # Uses the defined STATUS_CHOICE tuples.
        default='TODO' # Sets the default status for a new task to 'TODO'.
    )
    """
    The current completion status of the task.
    It can be 'To Do', 'In Progress', or 'Done'.
    """
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, # References the default User model.
        on_delete=models.CASCADE, # If the owner user is deleted, all their tasks will also be deleted.
        related_name='tasks' # Allows accessing all tasks for a user via `user.tasks.all()`.
    )
    """
    A foreign key relationship to the User model.
    This field indicates which user owns this specific task.
    Crucial for implementing per-user task management.
    """
    labels = models.ManyToManyField(Label, blank=True, related_name='tasks')
    """
    A many-to-many relationship with the Label model.
    This allows a single task to be associated with multiple labels,
    and a single label to be associated with multiple tasks.
    `blank=True` means a task can exist without any labels assigned.
    `related_name='tasks'` allows accessing all tasks for a label via `label.tasks.all()`.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    """
    Automatically sets the timestamp when the task is first created.
    It will not be updated on subsequent modifications.
    """
    updated_at = models.DateTimeField(auto_now=True)
    """
    Automatically updates the timestamp whenever the task object is saved.
    """

    def __str__(self):
        """
        String representation of the Task object.
        Returns the title of the task, useful for display and debugging.
        """
        return self.title