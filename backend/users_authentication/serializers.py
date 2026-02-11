# serializers.py
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'virtual_balance', 'created_at']
        read_only_fields = ['id', 'virtual_balance', 'created_at']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    password_confirmation = serializers.CharField(write_only=True, min_length=6)
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'password_confirmation']
    
    def validate(self, data):
        if data['password'] != data['password_confirmation']:
            raise serializers.ValidationError({"password": "Passwords don't match"})
        return data
    
    def create(self, validated_data):
        # Remove password_confirmation before creating user
        validated_data.pop('password_confirmation')
        # Hash the password
        validated_data['password'] = make_password(validated_data['password'])
        return CustomUser.objects.create(**validated_data)

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)