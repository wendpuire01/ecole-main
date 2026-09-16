"""
URL configuration for school_manager project.
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.views.static import serve as static_serve

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('portal/', include('school_portal.urls')),
    path('finance/', include('school_finance.urls')),
]

# Les fichiers media (logo, photos...) sont servis par Django dans tous les
# environnements. On ne peut pas utiliser le raccourci static() ici : il
# renvoie une liste vide dès que DEBUG=False, donc aucune route n'était
# jamais créée en production (sans Nginx devant, rien d'autre ne sert
# /media/). On appelle donc directement la vue serve().
urlpatterns += [
    re_path(
        r'^%s(?P<path>.*)$' % settings.MEDIA_URL.lstrip('/'),
        static_serve,
        {'document_root': settings.MEDIA_ROOT},
    ),
]

# Les fichiers static sont servis par WhiteNoise en production, donc
# uniquement nécessaire ici en développement.
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
