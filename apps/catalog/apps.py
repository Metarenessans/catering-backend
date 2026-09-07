from django.apps import AppConfig


class CatalogConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.catalog"
    verbose_name = "Каталог"

    def ready(self):
        self._setup_admin_ordering()
        import apps.catalog.signals  # noqa

    def _setup_admin_ordering(self):
        from django.contrib import admin

        # Желаемый порядок приложений в боковом меню и на главной админки
        APPS_ORDER = [
            "catalog",
            "orders",
            "menu_requests",
            "company",
            "system_settings",
            "auth",
            "faq",
            "token_blacklist",
        ]

        # Желаемый порядок моделей внутри приложений
        APP_MODELS_ORDER = {
            "catalog": ["Section", "Category", "Product"],
            "orders": ["Order", "EmailSubscriber", "TelegramSubscriber"],
            "menu_requests": ["MenuRequest", "EventFormat", "AdditionalService"],
        }

        original_get_app_list = admin.AdminSite.get_app_list

        def custom_get_app_list(self_admin, request, app_label=None):
            app_list = original_get_app_list(self_admin, request, app_label)

            # Сортировка приложений
            app_list.sort(
                key=lambda a: (
                    APPS_ORDER.index(a["app_label"])
                    if a["app_label"] in APPS_ORDER
                    else len(APPS_ORDER)
                )
            )

            # Сортировка моделей внутри приложений
            for app in app_list:
                label = app.get("app_label")
                if label in APP_MODELS_ORDER:
                    order_list = APP_MODELS_ORDER[label]
                    app["models"].sort(
                        key=lambda m: (
                            order_list.index(m["object_name"])
                            if m["object_name"] in order_list
                            else len(order_list)
                        )
                    )
            return app_list

        if not getattr(admin.AdminSite, "_custom_ordering_patched", False):
            admin.AdminSite.get_app_list = custom_get_app_list
            admin.AdminSite._custom_ordering_patched = True
