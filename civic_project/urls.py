from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('complaints/', include('complaints.urls')),   # FIX: was missing
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # FIX: media files
