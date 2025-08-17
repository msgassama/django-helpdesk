from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from base.models import Profile


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    profile = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                 'password', 'is_active', 'date_joined', 'profile']
        extra_kwargs = {
            'password': {'write_only': True},
        }
    
    def get_profile(self, obj):
        try:
            profile = obj.profile
            request = self.context.get('request')
            photo_url = None
            if profile.photo and request:
                photo_url = request.build_absolute_uri(profile.photo.url)
            
            return {
                'role': profile.role,
                'role_display': profile.get_role_display(),
                'phone': profile.phone,
                'department': profile.department,
                'department_display': profile.get_department_display(),
                'photo': photo_url,
                'full_name': profile.get_full_name(),
            }
        except Profile.DoesNotExist:
            return None
    
    # Cette méthode create() permet une création basique de User sans gestion du profil
    # Elle n'est pas utilisée car on préfère UserCreateSerializer qui gère le profil
    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data['password'] = make_password(password)
        user = User.objects.create(**validated_data)
        return user
    
    def update(self, instance, validated_data):
        if 'password' in validated_data:
            password = validated_data.pop('password')
            validated_data['password'] = make_password(password)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class ProfileSerializer(serializers.ModelSerializer):
    user_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Profile
        fields = ['id', 'role', 'phone', 'department', 'photo', 
                 'created_at', 'updated_at', 'user_info']
    
    def get_user_info(self, obj):
        return {
            'id': obj.user.id,
            'username': obj.user.username,
            'email': obj.user.email,
            'first_name': obj.user.first_name,
            'last_name': obj.user.last_name,
            'is_active': obj.user.is_active,
        }


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=Profile.ROLE_CHOICES, required=False, default='user')
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    department = serializers.ChoiceField(choices=Profile.DEPARTMENT_CHOICES, required=False, default='other')
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 
                 'password', 'password_confirm', 'role', 'phone', 'department']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Les mots de passe ne correspondent pas.")
        return attrs
    
    def create(self, validated_data):
        # Extraire les données du profil
        role = validated_data.pop('role', 'user')
        phone = validated_data.pop('phone', '')
        department = validated_data.pop('department', 'other')
        validated_data.pop('password_confirm')
        
        # Créer l'utilisateur (le signal va créer automatiquement le Profile)
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        
        # Mettre à jour le profil créé par le signal
        profile = user.profile
        profile.role = role
        profile.phone = phone
        profile.department = department
        profile.save()
        
        return user