from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.urls import include


urlpatterns = [
    path("admin/", admin.site.urls),
    path("__debug__/", include("debug_toolbar.urls")),
    path("api/", include("haleygg.urls")),
    path("api-auth/", include("rest_framework.urls")),
    path("api-auth/account/", include("account.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
