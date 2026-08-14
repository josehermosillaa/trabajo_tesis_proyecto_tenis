from rest_framework import serializers

from .models import (
    Category,
    Competition,
    CompetitionCategory,
    Player,
)

class PlayerSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        source="user.email",
        read_only=True
    )
    class Meta:
        model = Player
        fields = [
            "id",
            "user",
            "rut",
            "first_name",
            "last_name",
            "birth_date",
            "email",
            "phone",
        ]
        read_only_fields = ["id"]
        

class CompetitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competition
        fields = [
            "id",
            "name",
            "type",
            "start_date",
            "end_date",
            "status",
            "registration_deadline",
        ]
        read_only_fields = ["id"]
        
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            "id",
            "name",
        ]
        read_only_fields = ["id"]
        

class CompetitionCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = CompetitionCategory
        fields = [
            "id",
            "competition",
            "category",
            "max_players",
            "minimum_players",
        ]
        read_only_fields = ["id"]

    def validate(self, data):
        max_players = data.get("max_players")
        minimum_players = data.get("minimum_players")

        if (
            max_players is not None
            and minimum_players is not None
            and minimum_players > max_players
        ):
            raise serializers.ValidationError(
                {
                    "minimum_players": (
                        "El número mínimo de jugadores "
                        "no puede ser mayor al máximo."
                    )
                }
            )

        return data