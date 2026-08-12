from rest_framework import serializers

from .models import Category, Competition, Player

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