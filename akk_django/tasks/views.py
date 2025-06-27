# Logica de las vistas de la API

from rest_framework import viewsets, permissions, status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from .models import Task, Label
from .serializers import TaskSerializer, LabelSerializer


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permiso personalizado para permitir que solo los propietarios de un objeto lo editen o eliminen.
    Los métodos seguros (GET, HEAD, OPTIONS) siempre están permitidos.
    """
    def has_object_permission(self, request, view, obj):
        # Los permisos de lectura están permitidos para cualquier solicitud.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Los permisos de escritura solo están permitidos para el propietario del objeto.
        return obj.owner == request.user
    

class TaskViewSet(viewsets.ModelViewSet):
    # --- Añade esta línea ---
    queryset = Task.objects.all() 
    # -------------------------
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        """
        Retorna el queryset de tareas. Si el usuario es staff, retorna todas las tareas.
        De lo contrario, retorna solo las tareas que le pertenecen.
        """
        if self.request.user.is_staff:
            return Task.objects.all()
        return Task.objects.filter(owner=self.request.user)
    
    
    def perform_create(self, serializer):
        """
        Al crear una tarea, asigna el propietario y maneja las etiquetas.
        Asegura que las etiquetas existan y pertenezcan al usuario.
        """
        # Obtener las IDs de las etiquetas del request, si existen.
        labels_ids = self.request.data.get('label_ids', []) 
        
        # Verificar que las etiquetas existan y pertenezcan al usuario actual.
        # Si labels_ids es None o no es iterable, se convierte a una lista vacía
        labels_ids = labels_ids if isinstance(labels_ids, list) else [] 
        
        # Filtra las etiquetas válidas que el usuario posee
        valid_labels = Label.objects.filter(id__in=labels_ids, owner=self.request.user)
        
        # Si la cantidad de etiquetas encontradas no coincide con las IDs proporcionadas,
        # significa que algunas etiquetas no existen o no pertenecen al usuario.
        if len(valid_labels) != len(labels_ids):
            raise ValidationError(
                {"label_ids": "Una o más etiquetas no encontradas o no pertenecen al usuario autenticado."}
            )
        
        # Guarda la tarea asignando el propietario y las etiquetas.
        serializer.save(owner=self.request.user, labels=valid_labels)


    def perform_update(self, serializer):
        """
        Al actualizar una tarea, maneja los permisos para cambiar el propietario
        y actualiza las etiquetas si se proporcionan.
        """
        # Evita que un usuario no-staff cambie el propietario de una tarea.
        if 'owner_id' in self.request.data and serializer.instance.owner != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied("No tiene permiso para cambiar el propietario de esta tarea.")
        
        # Obtener las IDs de las etiquetas del request.
        # Usa .get('label_ids') sin un valor por defecto para saber si el cliente lo envió o no.
        labels_ids = self.request.data.get('label_ids') 
        
        # Si 'label_ids' está presente en el request (incluso si es una lista vacía), procesa las etiquetas.
        if labels_ids is not None:
            # Asegúrate de que labels_ids sea una lista
            if not isinstance(labels_ids, list):
                raise ValidationError({"label_ids": "El formato de label_ids debe ser una lista."})

            # Filtra las etiquetas válidas que el usuario posee.
            valid_labels = Label.objects.filter(id__in=labels_ids, owner=self.request.user)
            
            # Valida que todas las etiquetas proporcionadas sean válidas y pertenezcan al usuario.
            if len(valid_labels) != len(labels_ids):
                raise ValidationError(
                    {"label_ids": "Una o más etiquetas no encontradas o no pertenecen al usuario autenticado."}
                )
            
            # Guarda la tarea con las etiquetas actualizadas.
            serializer.save(labels=valid_labels)
        else:
            # Si 'label_ids' no se proporcionó en el request, guarda sin modificar las etiquetas.
            serializer.save()


class LabelViewSet(viewsets.ModelViewSet):
    # --- Añade esta línea ---
    queryset = Label.objects.all()
    # -------------------------
    serializer_class = LabelSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        """
        Retorna el queryset de etiquetas. Si el usuario es staff, retorna todas las etiquetas.
        De lo contrario, retorna solo las etiquetas que le pertenecen.
        """
        if self.request.user.is_staff:
                return Label.objects.all()
        return Label.objects.filter(owner=self.request.user)
    
    def perform_create(self, serializer):
        """
        Al crear una etiqueta, asigna el propietario y valida que el nombre sea único para el usuario.
        """
        name = serializer.validated_data.get('name')
        if Label.objects.filter(name=name, owner=self.request.user).exists():
            raise ValidationError({'name': 'Una etiqueta con este nombre ya existe para este usuario.'}, code='unique')
        serializer.save(owner=self.request.user)


    def perform_update(self, serializer):
        """
        Al actualizar una etiqueta, maneja los permisos para cambiar el propietario
        y valida que el nombre de la etiqueta siga siendo único para el usuario.
        """
        # Evita que un usuario no-staff cambie el propietario de una etiqueta.
        if 'owner_id' in self.request.data and serializer.instance.owner != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied("No tiene permiso para cambiar el propietario de esta etiqueta.")

        name = serializer.validated_data.get('name')
        # Si se proporciona un nuevo nombre y es diferente al actual, valida unicidad.
        if name and name != serializer.instance.name:
            if Label.objects.filter(name=name, owner=self.request.user).exclude(id=serializer.instance.id).exists():
                raise ValidationError({'name': 'Una etiqueta con este nombre ya existe para este usuario.'}, code='unique')
        serializer.save()