from rest_framework.permissions import BasePermission


class IsAdminUser(BasePermission):
    """
    Permission pour les administrateurs uniquement
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.profile.has_admin_access()
        )


class IsTechnicianOrAbove(BasePermission):
    """
    Permission pour technicien, manager et admin
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.profile.has_technician_access()
        )


class CanManageIncidents(BasePermission):
    """
    Permission pour gérer les incidents (manager et admin)
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.profile.can_manage_incidents()
        )


class IsOwnerOrAdmin(BasePermission):
    """
    Permission pour propriétaire de l'objet ou admin
    """
    def has_object_permission(self, request, view, obj):
        if not (request.user and request.user.is_authenticated):
            return False
        
        # Admin peut tout faire
        if request.user.profile.has_admin_access():
            return True
        
        # Propriétaire peut accéder et ses propres données
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        return False


class UserCRUDPermission(BasePermission):
    """
    Permission spécifique pour les opérations CRUD sur les utilisateurs
    """
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        
        # Lecture : laisser has_object_permission décider pour l'accès par objet
        if request.method in ['GET']:
            return True
        
        # Création/Suppression : admin uniquement
        if request.method in ['POST', 'DELETE']:
            return request.user.profile.has_admin_access()
        
        # Modification : laisser has_object_permission décider
        if request.method in ['PUT']:
            return True
        
        return False
    
    def has_object_permission(self, request, view, obj):
        if not (request.user and request.user.is_authenticated):
            return False
        
        # Admin peut tout faire
        if request.user.profile.has_admin_access():
            return True
        
        # Technicien+ peut voir tous les profils
        if request.method in ['GET'] and request.user.profile.has_technician_access():
            return True
        
        # Tout user peut voir/modifier son propre profil
        if request.method in ['GET', 'PUT']:
            return obj == request.user
        
        return False