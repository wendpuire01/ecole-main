"""
URL configuration for school_manager project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('portal/', include('school_portal.urls')),
    path('finance/', include('school_finance.urls')),
]

# Les fichiers media (logo, photos...) sont servis par Django dans tous les
# environnements : sans Nginx devant (docker-compose.yml simple), rien
# d'autre ne les sert en production puisque DEBUG=False.
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Les fichiers static sont servis par WhiteNoise en production, donc
# uniquement nécessaire ici en développement.
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
