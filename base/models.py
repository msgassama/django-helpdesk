from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Profile(models.Model):


    ROLE_CHOICES = [
        ('admin', 'Administrateur'),
        ('technician', 'Technicien'),
        ('manager', 'Manager'),
        ('user', 'Utilisateur'),
    ]

    DEPARTMENT_CHOICES = [
        ('it', 'Informatique'),
        ('hr', 'Ressources Humaines'), 
        ('finance', 'Finance'),
        ('operations', 'Opérations'),
        ('support', 'Support Client'),
        ('other', 'Autre'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Utilisateur', help_text="Référence vers l'utilisateur Django associé")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user', verbose_name="Rôle", help_text="Rôle de l'utilisateur dans le système")
    photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True, default='profile_photos/default.png', verbose_name="Photo de profil", help_text="Photo de profil de l'utilisateur (optionnel)")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone", help_text="Numéro de téléphone de l'utilisateur")
    department = models.CharField(max_length=20, choices=DEPARTMENT_CHOICES, default='other', verbose_name="Département", help_text="Département d'affectation")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de mise à jour")

    class Meta:
        verbose_name = "Profil Utilisateur"
        verbose_name_plural = "Profils Utilisateurs"
        ordering = ['user__username']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"
    
    def get_full_name(self):
        full_name = f"{self.user.first_name} {self.user.last_name}".strip()
        return full_name if full_name else self.user.username
    
    def has_admin_access(self):
        return self.role == 'admin' or self.user.is_superuser
    
    def has_technician_access(self):
        return self.role in ['technician', 'manager', 'admin'] or self.user.is_superuser
    

