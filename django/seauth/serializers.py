# from django.contrib.auth.models import User
from rest_framework import serializers
from accounts.models import CustomUser

class LoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField()


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['email', 'password']
