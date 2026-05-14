from django.contrib import admin
from .models import FaqItem


@admin.register(FaqItem)
class FaqItemAdmin(admin.ModelAdmin):
    list_display = ["question", "order", "is_active"]
    list_editable = ["order", "is_active"]
    search_fields = ["question"]
    ordering = ["order"]
