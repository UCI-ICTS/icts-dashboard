#!/usr/bin/env python
# authentication/services.py

from rest_framework import serializers
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.models import User


class UserInputSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'is_superuser', 'is_staff', 'date_joined']
        extra_kwargs = {
            'username': {'required': False},  # allow username to be auto-set
            'date_joined': {'read_only': True},
        }

    def create(self, validated_data):
        email = validated_data.get("email")
        if not email:
            raise serializers.ValidationError({"email": "This field is required."})

        # Auto-generate username from email (allowing dots, etc.)
        base_username = email.split("@")[0]
        username = base_username
        counter = 1

        # Make sure the username is unique
        while User.objects.filter(username=username).exists():
            username = f"{base_username}.{counter}"
            counter += 1

        password = validated_data.pop('password', None)
        user = User(username=username, **validated_data)

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance



class UserOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'is_superuser', 'is_staff', 'date_joined']
        read_only_fields = fields


class CustomAuthentication(BaseAuthentication):
    """
    Custom JSON Web Token Authentication class that supports different types 
    of tokens including Bearer tokens from various issuers like ORCID, Google,
    and the BioCompute Portal.

    Methods:
    authenticate(self, request): 
        Authenticates the request based on the 'Authorization' header containing
        either 'Bearer' or 'Token' type credentials.

    Raises:
        AuthenticationFailed: If the token is invalid, expired, or the issuer is not recognized.
    """
    def authenticate(self, request):
        # Extract the token from the Authorization header
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return None  # No authentication performed

        # Ensure the header contains a Bearer token
        try:
            prefix, token = auth_header.split()
            if prefix.lower() != 'bearer':
                raise AuthenticationFailed("Invalid token prefix.")
        except ValueError:
            raise AuthenticationFailed("Invalid Authorization header format.")

        # Validate the token using SimpleJWT's AccessToken class
        try:
            decoded_token = AccessToken(token)  # Decode and validate the token
        except Exception as e:
            raise AuthenticationFailed(f"Invalid or expired token: {str(e)}")

        # Retrieve the user associated with the token
        try:
            user_id = decoded_token.get('user_id')
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise AuthenticationFailed("User not found.")
        
        # Return the user and the token
        return user, token
