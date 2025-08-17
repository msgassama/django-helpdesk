from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import get_object_or_404
from .serializers import UserSerializer, UserCreateSerializer, ProfileSerializer
from base.models import Profile


@api_view(['GET'])
def getRoutes(request):
    """
    Point d'entrée de l'API qui retourne la liste des routes disponibles.
    
    Cette vue publique fournit une documentation de base des endpoints
    disponibles dans l'API pour aider les développeurs.
    """
    routes = [
        '/api/token/',
        '/api/token/refresh/',
        '/api/incidents/',
        '/api/incidents/<id>/',
        '/api/users/',
        '/api/users/<id>/',
        '/api/profiles/',
        '/api/notes/',
    ]
    return Response(routes)


@api_view(['GET', 'POST'])
def user_list_create(request):
    if request.method == 'GET':
        users = User.objects.all().select_related('profile')
        serializer = UserSerializer(users, many=True, context={'request': request})
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                user = serializer.save()
                return Response(
                    UserSerializer(user, context={'request': request}).data, 
                    status=status.HTTP_201_CREATED
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def user_detail(request, pk):
    user = get_object_or_404(User.objects.select_related('profile'), pk=pk)
    
    if request.method == 'GET':
        serializer = UserSerializer(user, context={'request': request})
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        # Séparer les données user et profile
        user_data = {}
        profile_data = {}
        
        for key, value in request.data.items():
            if key in ['username', 'email', 'first_name', 'last_name', 'is_active', 'password']:
                user_data[key] = value
            elif key in ['role', 'phone', 'department', 'photo']:
                profile_data[key] = value
        
        with transaction.atomic():
            # Mettre à jour l'utilisateur
            if user_data:
                user_serializer = UserSerializer(user, data=user_data, partial=True)
                if user_serializer.is_valid():
                    user_serializer.save()
                else:
                    return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            # Mettre à jour le profil
            if profile_data:
                try:
                    profile = user.profile
                    profile_serializer = ProfileSerializer(profile, data=profile_data, partial=True)
                    if profile_serializer.is_valid():
                        profile_serializer.save()
                    else:
                        return Response(profile_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                except Profile.DoesNotExist:
                    # Créer le profil s'il n'existe pas
                    profile_data['user'] = user.id
                    profile_serializer = ProfileSerializer(data=profile_data)
                    if profile_serializer.is_valid():
                        profile_serializer.save()
                    else:
                        return Response(profile_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            # Retourner les données mises à jour
            updated_user = User.objects.select_related('profile').get(pk=user.pk)
            return Response(UserSerializer(updated_user, context={'request': request}).data)
    
    elif request.method == 'DELETE':
        # Vérifier si l'utilisateur peut être supprimé
        if user.is_superuser:
            return Response(
                {'error': 'Impossible de supprimer un superutilisateur'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        if user == request.user:
            return Response(
                {'error': 'Vous ne pouvez pas supprimer votre propre compte'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)