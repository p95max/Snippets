from django.templatetags.static import static
from django.views.generic import RedirectView
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from debug_toolbar.toolbar import debug_toolbar_urls
from django.conf.urls.static import static as static_serve

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('MainApp.urls', namespace='MainApp')),

    path('favicon.ico', RedirectView.as_view(url=static('media/favicon.svg'))),
] + debug_toolbar_urls()

if settings.DEBUG:
    urlpatterns += static_serve(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static_serve(settings.STATIC_URL, document_root=settings.STATIC_ROOT)