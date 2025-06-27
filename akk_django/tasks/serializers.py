# Serializadores para la API

from rest_framework import serializers
from .models import Task, Label
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username'] # 'field' debe ser 'fields'

class LabelSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    owner_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='owner', write_only=True, required=False
    )

    class Meta:
        model = Label # Corregido 'modek' a 'model'
        fields = ['id', 'name', 'owner', 'owner_id']
        read_only_fields = ['owner'] # Corregido 'ready_only_fields' a 'read_only_fields'
    
class TaskSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    owner_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='owner', write_only=True, required=False
    )
    # Cambiado 'label' a 'labels' para coincidir con el nombre del campo ManyToManyField en el modelo
    labels = LabelSerializer(many=True, read_only=True) 
    # Cambiado 'label_id' a 'label_ids' y 'source' a 'labels' para coincidir con el campo del modelo
    label_ids = serializers.PrimaryKeyRelatedField( 
        many=True, queryset=Label.objects.all(), source='labels', write_only=True, required=False
    )

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'completion_status', # Corregido 'titel' a 'title'
            'owner', 'owner_id', 'labels', 'label_ids', # 'label_ids' ahora es el campo write_only
            'created_at', 'updated_at'
        ]

        read_only_fields = ['created_at', 'updated_at', 'owner']