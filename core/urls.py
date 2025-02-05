from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("products/", include("products.urls")),
]

# Swagger/ReDoc API documentation endpoints for DEBUG mode only
if settings.DEBUG:
    urlpatterns += [
        path(
            "",
            SpectacularSwaggerView.as_view(url_name="schema"),
            name="swagger-ui",
        ),
        path(
            "schema/",
            SpectacularAPIView.as_view(api_version="v1"),
            name="schema",
        ),
        path(
            "redoc/",
            SpectacularRedocView.as_view(url_name="schema"),
            name="redoc",
        ),
    ]
