from django.contrib import admin
from adminsortable2.admin import SortableAdminMixin
from .models import FaqItem


@admin.register(FaqItem)
class FaqItemAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ["question", "order", "is_active"]
    list_editable = ["is_active"]
    search_fields = ["question"]
    ordering = ["order"]

