#!/usr/bin/env python
# authentication/services.py

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.models import User


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

class CustomObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['name'] = user.username
        # ...

        return token