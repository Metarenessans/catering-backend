from django.contrib import admin
from .models import CompanyInfo


@admin.register(CompanyInfo)
class CompanyInfoAdmin(admin.ModelAdmin):
    list_display = ["company_name", "phone_number", "email", "updated_at"]
    readonly_fields = ["updated_at"]

    def has_add_permission(self, request):
        """Разрешаем создание только если записи нет."""
        return not CompanyInfo.objects.exists()

    def has_delete_permission(self, request, obj=None):
        """Запрещаем удаление singleton-записи."""
        return False
