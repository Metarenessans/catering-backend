"""
URL configuration for catering_backend project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

# Скрываем неиспользуемый раздел "TOKEN BLACKLIST" из интерфейса админки
try:
    from rest_framework_simplejwt.token_blacklist.models import (
        OutstandingToken,
        BlacklistedToken,
    )

    admin.site.unregister(OutstandingToken)
    admin.site.unregister(BlacklistedToken)
except Exception:
    pass

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),

    # API v1
    path("api/v1/catalog/", include("apps.catalog.urls")),
    path("api/v1/orders/", include("apps.orders.urls")),
    path("api/v1/menu-requests/", include("apps.menu_requests.urls")),
    path("api/v1/faq/", include("apps.faq.urls")),
    path("api/v1/company/", include("apps.company.urls")),
    path("api/v1/system-settings/", include("apps.system_settings.urls")),
    path("api/v1/blog/", include("apps.blog.urls")),

    # JWT Auth
    path("api/v1/auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/v1/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/v1/auth/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
]

# OpenAPI / Swagger — только в режиме разработки
if settings.DEBUG:
    urlpatterns += [
        path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
        path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
        path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

