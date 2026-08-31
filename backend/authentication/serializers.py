from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
)


class RoleTokenObtainPairSerializer(
    TokenObtainPairSerializer
):

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = user.role.name

        return token
