from django.contrib.auth.models import User
from .models import Profile
from django.dispatch import receiver
from django.db.models.signals import post_save


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal pour créer automatiquement un profil utilisateur.
    
    Ce signal se déclenche après la création d'un nouvel utilisateur
    et crée automatiquement son profil associé.
    
    Args:
        sender: Le modèle User
        instance: L'instance de l'utilisateur créé
        created (bool): True si l'utilisateur vient d'être créé
        **kwargs: Arguments supplémentaires
    """
    if created:
        # Déterminer le rôle basé sur les permissions de l'utilisateur
        if instance.is_superuser:
            role = 'admin'
        elif instance.is_staff:
            role = 'manager'
        else:
            role = 'user'
        
        Profile.objects.create(user=instance, role=role)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Signal pour sauvegarder le profil utilisateur.
    
    Ce signal se déclenche après la sauvegarde d'un utilisateur
    et sauvegarde également son profil si il existe.
    
    Args:
        sender: Le modèle User
        instance: L'instance de l'utilisateur
        **kwargs: Arguments supplémentaires
    """
    if hasattr(instance, 'profile'):
        # Mettre à jour seulement pour les promotions basées sur les permissions Django
        if instance.is_superuser and instance.profile.role != 'admin':
            instance.profile.role = 'admin'
        elif instance.is_staff and not instance.is_superuser and instance.profile.role not in ['admin', 'manager']:
            instance.profile.role = 'manager'
        
        instance.profile.save()