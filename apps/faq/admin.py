from django import forms
from django.contrib import admin
from adminsortable2.admin import SortableAdminMixin
from .models import FaqItem
from .widgets import StringListWidget
from apps.catalog.mixins import MakeFirstAdminMixin


class FaqItemForm(forms.ModelForm):
    class Meta:
        model = FaqItem
        fields = "__all__"
        widgets = {
            "answer_items": StringListWidget(),
        }


@admin.register(FaqItem)
class FaqItemAdmin(SortableAdminMixin, MakeFirstAdminMixin, admin.ModelAdmin):
    form = FaqItemForm
    list_display = ["order", "question", "is_active"]
    list_editable = ["is_active"]
    search_fields = ["question"]
    ordering = ["order"]

    class Media:
        css = {
            "all": ("admin/css/sortable_custom.css",)
        }



