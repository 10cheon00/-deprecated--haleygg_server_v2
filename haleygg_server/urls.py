from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.urls import include

urlpatterns = []

if settings.DEBUG:
    urlpatterns += path("__debug__/", include("debug_toolbar.urls"))

urlpatterns += [
    path("admin/", admin.site.urls),
    path("api/", include("haleygg.urls")),
    path("api/auth/", include("haleygg_auth.urls")),
    path("api/elo/", include("haleygg_elo.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
