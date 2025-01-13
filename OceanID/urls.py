from django.contrib import admin
from django.urls import path, include
from api.views import home  # Import the home view
from django.views.generic.base import RedirectView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', home, name='home'),
    path('', include('auth_app.urls')),
    path('admin/', admin.site.urls),
    path('auth_app/', include('auth_app.urls')),
    path('api/', include('api.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)