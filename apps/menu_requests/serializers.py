from rest_framework import serializers
from .models import (
    MenuRequest,
    AdditionalService,
    EventFormat,
    CalculatePageSettings,
    CalculateFeature,
    CalculateBudgetOption,
    CalculateFoodOption,
    CalculateStep,
    CalculateFAQ,
)
from ..catalog.serializers import ProductSerializer

import datetime


class EventFormatSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventFormat
        fields = ["id", "name", "order", "is_active"]

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret["id"] = str(ret["id"])
        return ret


class AdditionalServiceSerializer(serializers.ModelSerializer):
    linked_product = ProductSerializer(read_only=True)

    class Meta:
        model = AdditionalService
        fields = ["id", "label", "description", "order", "is_active", "linked_product"]

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret["id"] = str(ret["id"])
        return ret


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
            "budget",
            "date",
            "food_preferences",
            "additional_services",
            "name",
            "phone",
            "contact_method",
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
    guests = serializers.CharField(max_length=100, required=False, allow_blank=True)
    budget = serializers.CharField(max_length=100, required=False, allow_blank=True, default="")
    date = serializers.DateField(required=False, allow_null=True)
    additional = serializers.ListField(
        child=serializers.CharField(),
        default=list,
        help_text="Список строк: ID услуг и/или наименования блюд",
    )
    name = serializers.CharField(max_length=200)
    phone = serializers.CharField(max_length=30)
    contact_method = serializers.CharField(max_length=50, default="Позвонить мне")
    consent = serializers.BooleanField()

    def validate_date(self, value):
        if not value:
            return value
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


class CalculateFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalculateFeature
        fields = ["id", "icon", "title", "subtitle", "order"]


class CalculateStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalculateStep
        fields = ["id", "step", "title", "text", "order"]


class CalculateFAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalculateFAQ
        fields = ["id", "question", "answer", "order"]


class CalculatePageSettingsSerializer(serializers.ModelSerializer):
    features = serializers.SerializerMethodField()
    budget_options = serializers.SerializerMethodField()
    food_options = serializers.SerializerMethodField()
    additional_services = serializers.SerializerMethodField()
    steps = serializers.SerializerMethodField()
    faqs = serializers.SerializerMethodField()

    class Meta:
        model = CalculatePageSettings
        fields = [
            "hero_badge",
            "hero_title",
            "hero_description",
            "features",
            "budget_options",
            "food_options",
            "additional_services",
            "steps_title",
            "steps_subtitle",
            "steps",
            "faq_title",
            "faq_subtitle",
            "faqs",
            "seo_title",
            "seo_description",
            "updated_at",
        ]

    def get_features(self, obj):
        active = obj.features.filter(is_active=True).order_by("order")
        return CalculateFeatureSerializer(active, many=True).data

    def get_budget_options(self, obj):
        active = obj.budget_options.filter(is_active=True).order_by("order")
        return list(active.values_list("name", flat=True))

    def get_food_options(self, obj):
        active = obj.food_options.filter(is_active=True).order_by("order")
        return list(active.values_list("name", flat=True))

    def get_additional_services(self, obj):
        from .models import AdditionalService
        # Return services associated with settings, or active services
        services = AdditionalService.objects.filter(is_active=True).order_by("order")
        return AdditionalServiceSerializer(services, many=True).data

    def get_steps(self, obj):
        active = obj.steps.filter(is_active=True).order_by("order")
        return CalculateStepSerializer(active, many=True).data

    def get_faqs(self, obj):
        active = obj.faqs.filter(is_active=True).order_by("order")
        return CalculateFAQSerializer(active, many=True).data
