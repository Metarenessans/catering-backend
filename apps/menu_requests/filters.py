import django_filters
from .models import MenuRequest


class MenuRequestFilter(django_filters.FilterSet):
    status = django_filters.ChoiceFilter(choices=MenuRequest.StatusChoices.choices)
    date_from = django_filters.DateFilter(field_name="date", lookup_expr="gte")
    date_to = django_filters.DateFilter(field_name="date", lookup_expr="lte")
    created_from = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="gte")
    created_to = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="lte")

    class Meta:
        model = MenuRequest
        fields = ["status", "date_from", "date_to", "format"]
