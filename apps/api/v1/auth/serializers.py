from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from apps.auth_app.models import UserProfile
import re

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'password')
        read_only_fields = ('id',)
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def validate_password(self, password):
        """
        Validate password strength requirements:
        - At least 8 characters
        - At least one lowercase letter
        - At least one uppercase letter  
        - At least one number
        - At least one special character
        """
        errors = []
        
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")
        
        if not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
            
        if not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
            
        if not re.search(r'\d', password):
            errors.append("Password must contain at least one number")
            
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', password):
            errors.append("Password must contain at least one special character (!@#$%^&*)")
        
        if errors:
            raise serializers.ValidationError(errors)
            
        return password
    
    def create(self, validated_data):
        # Hash the password properly
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = (
            'user', 'profession', 'research_field', 'institution', 'bio',
            'is_academic_verified', 'email_notifications', 'weekly_digest',
            'profile_completed', 'profile_completion_date', 'last_login_at',
            'total_login_count', 'created_at', 'updated_at'
        )
        read_only_fields = ('is_academic_verified', 'profile_completed', 
                          'profile_completion_date', 'last_login_at', 
                          'total_login_count', 'created_at', 'updated_at')


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)


class TokenSerializer(serializers.Serializer):
    access_token = serializers.CharField()
    refresh_token = serializers.CharField()
    token_type = serializers.CharField()
    expires_in = serializers.IntegerField()


class RefreshTokenSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(required=True)