from rest_framework import serializers
from .models import MenuRequest, AdditionalService, EventFormat

import datetime


class EventFormatSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventFormat
        fields = ["id", "name", "order", "is_active"]


class AdditionalServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdditionalService
        fields = ["id", "label", "description", "order", "is_active"]


class MenuRequestSerializer(serializers.ModelSerializer):
    """
    Полный сериализатор заявки (для admin).
    """
    class Meta:
        model = MenuRequest
        fields = [
            "id",
            "format",
            "guests",
            "date",
            "food_preferences",
            "additional_services",
            "name",
            "phone",
            "consent",
            "status",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class MenuRequestCreateSerializer(serializers.Serializer):
    """
    Входной формат из MenuPopup (MenuFormData).
    Минимальная валидация для публичного endpoint.
    """
    format = serializers.CharField(max_length=100)
    guests = serializers.IntegerField(min_value=1)
    date = serializers.DateField()
    additional = serializers.ListField(
        child=serializers.CharField(),
        default=list,
        help_text="Список строк: ID услуг и/или наименования блюд",
    )
    name = serializers.CharField(max_length=200)
    phone = serializers.CharField(max_length=30)
    consent = serializers.BooleanField()

    def validate_date(self, value):
        if value < datetime.date.today():
            raise serializers.ValidationError("Дата мероприятия не может быть в прошлом.")
        return value

    def validate_consent(self, value):
        if not value:
            raise serializers.ValidationError(
                "Необходимо дать согласие на обработку персональных данных."
            )
        return value

    def create(self, validated_data):
        additional = validated_data.pop("additional", [])

        # Разбиваем additional на услуги и предпочтения по блюдам
        food_keywords = {"Супы, бульоны", "Горячее", "Салаты", "Закуски", "Десерты"}
        food_preferences = [item for item in additional if item in food_keywords]
        service_ids = [item for item in additional if item not in food_keywords]

        return MenuRequest.objects.create(
            **validated_data,
            food_preferences=food_preferences,
            additional_services=service_ids,
        )


class MenuRequestStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuRequest
        fields = ["status", "notes"]
