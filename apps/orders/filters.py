import django_filters
from .models import Order


class OrderFilter(django_filters.FilterSet):
    status = django_filters.ChoiceFilter(choices=Order.StatusChoices.choices)
    created_from = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="gte")
    created_to = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="lte")
    min_total = django_filters.NumberFilter(field_name="final_price", lookup_expr="gte")
    max_total = django_filters.NumberFilter(field_name="final_price", lookup_expr="lte")

    class Meta:
        model = Order
        fields = ["status", "created_from", "created_to", "min_total", "max_total"]
