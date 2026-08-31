from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
)
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from .models import Role, User


class RoleTokenObtainPairSerializer(
    TokenObtainPairSerializer
):

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = user.role.name

        return token


class OrganizerSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password_confirmation = serializers.CharField(write_only=True, required=True)
    role = serializers.CharField(source="role.name", read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    first_name = serializers.CharField(required=True, allow_blank=False)
    last_name = serializers.CharField(required=True, allow_blank=False)
    email = serializers.EmailField(required=True, allow_blank=False)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "is_active",
            "role",
            "password",
            "password_confirmation",
        )
        read_only_fields = ("id", "is_active", "role")

    def validate(self, attrs):
        password = attrs.get("password")
        confirmation = attrs.pop("password_confirmation", None)

        if self.instance is None:
            if password != confirmation:
                raise serializers.ValidationError({
                    "password_confirmation": "Las contraseñas no coinciden."
                })

            candidate = User(
                username=attrs.get("username", ""),
                first_name=attrs.get("first_name", ""),
                last_name=attrs.get("last_name", ""),
                email=attrs.get("email", ""),
            )
            try:
                validate_password(password, user=candidate)
            except DjangoValidationError as error:
                raise serializers.ValidationError({
                    "password": list(error.messages)
                }) from error
        else:
            attrs.pop("password", None)

        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        organizer_role = Role.objects.get(name="Organizador")
        user = User(**validated_data, role=organizer_role)
        user.set_password(password)
        user.save()
        return user


class OrganizerActiveSerializer(serializers.Serializer):
    active = serializers.BooleanField()
