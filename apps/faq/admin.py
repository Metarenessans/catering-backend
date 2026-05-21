from django.contrib import admin
from adminsortable2.admin import SortableAdminMixin
from .models import FaqItem
from apps.catalog.mixins import MakeFirstAdminMixin


@admin.register(FaqItem)
class FaqItemAdmin(SortableAdminMixin, MakeFirstAdminMixin, admin.ModelAdmin):
    list_display = ["order", "question", "is_active"]
    list_editable = ["is_active"]
    search_fields = ["question"]
    ordering = ["order"]

    class Media:
        css = {
            "all": ("admin/css/sortable_custom.css",)
        }


