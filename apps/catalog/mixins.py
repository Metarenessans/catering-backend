from django.urls import path
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django.db import transaction, models


class MakeFirstAdminMixin:
    """
    Миксин для ModelAdmin, добавляющий кнопку "Сделать первым" в форме редактирования.
    При нажатии элемент перемещается на первую позицию (с нормализацией порядка остальных элементов).
    """
    change_form_template = "admin/change_form_with_make_first.html"
    sortable_group_by = None  # Имя поля (например, 'category') для фильтрации внутри группы

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "<path:object_id>/change/make-first/",
                self.admin_site.admin_view(self.make_first_view),
                name="%s_%s_make_first" % (self.model._meta.app_label, self.model._meta.model_name),
            ),
        ]
        return custom_urls + urls

    def make_first_view(self, request, object_id):
        obj = self.get_object(request, object_id)
        if obj is None:
            messages.error(request, "Объект не найден.")
            return redirect(f"admin:{self.model._meta.app_label}_{self.model._meta.model_name}_changelist")

        try:
            with transaction.atomic():
                # Имя поля сортировки (обычно 'order')
                order_field = getattr(self, "sortable_field_name", "order")

                # Фильтрация по группе, если задано (например, для товаров по категориям)
                filter_kwargs = {}
                group_field = getattr(self, "sortable_group_by", None)
                if group_field and hasattr(obj, group_field):
                    group_val = getattr(obj, group_field)
                    filter_kwargs[group_field] = group_val

                queryset = self.model.objects.filter(**filter_kwargs)

                # Временно задаём текущему объекту минимальный порядок 0
                setattr(obj, order_field, 0)
                obj.save(update_fields=[order_field])

                # Выстраиваем все элементы группы по порядку и переназначаем последовательно 1, 2, 3...
                sorted_objs = queryset.order_by(order_field, "id")
                for idx, item in enumerate(sorted_objs, start=1):
                    if getattr(item, order_field) != idx:
                        setattr(item, order_field, idx)
                        item.save(update_fields=[order_field])

            messages.success(request, f'Элемент "{obj}" успешно сделан первым в списке.')
        except Exception as e:
            messages.error(request, f"Ошибка при перемещении элемента: {str(e)}")

        return redirect(reverse(f"admin:{self.model._meta.app_label}_{self.model._meta.model_name}_changelist"))
