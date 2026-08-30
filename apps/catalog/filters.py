import django_filters
from .models import Product


class ProductFilter(django_filters.FilterSet):
    """
    Фильтры для продуктов.
    Поддерживает: категорию, раздел, диапазон цен, рекомендуемые и активные.
    """
    category = django_filters.CharFilter(
        field_name="category__slug",
        lookup_expr="exact",
        label="Категория (slug)",
    )
    section = django_filters.CharFilter(
        field_name="category__sections__slug",
        lookup_expr="exact",
        label="Раздел (slug)",
    )
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    is_featured = django_filters.BooleanFilter()
    is_active = django_filters.BooleanFilter()

    class Meta:
        model = Product
        fields = ["category", "section", "min_price", "max_price", "is_featured", "is_active"]
