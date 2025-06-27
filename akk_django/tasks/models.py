# Definicion de modelos task y label

from django.db import models
from django.conf import settings


class Label(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='labels'
    )
    class Meta:
        unique_together = ('name', 'owner',)

    def __str__(self):
        return self.name
    

class Task(models.Model):
    STATUS_CHOICE = [
        ('TODO', 'To Do'),
        ('IN_PROGRESS', 'IN Progress'),
        ('DONE', 'Done'),
    ]
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    completion_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICE,
        default='TODO'
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tasks'
    )
    labels = models.ManyToManyField(Label, blank=True, related_name='tasks')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title