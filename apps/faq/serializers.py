from rest_framework import serializers
from .models import FaqItem


class FaqItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FaqItem
        fields = ["id", "question", "answer_items", "order", "is_active"]

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret["answerItems"] = ret.pop("answer_items", [])
        return ret
