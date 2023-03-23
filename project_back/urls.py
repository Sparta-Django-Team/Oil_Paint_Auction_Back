# rest_framework
from rest_framework import permissions

# django
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# swagger
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
    openapi.Info(
        title="OIL PAINT API",
        default_version="v2",
        description="오완코 유화 프로젝트 API",
        terms_of_service="https://www.ourapp.com/policies/terms/",
        contact=openapi.Contact(email="wogur981208@gmail.com"),
        license=openapi.License(name="Owanco License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),
    
    # Apps
    path("", include("users.urls")),
    path("auctions/", include("auctions.urls")),
    path("paintings/", include("paintings.urls")),
    
    # Swagger
    path("", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("api/api.json/", schema_view.without_ui(cache_timeout=0), name="schema-swagger-json"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
