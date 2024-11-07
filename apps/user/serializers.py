from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "phone_number", "email", "password"]
        extra_kwargs = {
            "password": {"write_only": True}, # Password should not be returned in response
        }