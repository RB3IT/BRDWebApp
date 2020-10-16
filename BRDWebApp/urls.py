"""
Definition of urls for BRDWebApp.
"""

from datetime import datetime
from django.conf.urls import url
import django.contrib.auth.views

from inventory import forms
from . import settings

# Uncomment the next lines to enable the admin:
from django.conf.urls import include
from django.conf.urls.static import static
from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    url(r"^entities/", include("entities.urls")),
    url(r"^inventory/",include("inventory.urls")),
    url(r"^doors/", include("doors.urls")),
    url(r"^tools/", include("tools.urls")),
    url(r"^kiosk/", include("kiosk.urls")),
    url(r'^.*login/$',
        django.contrib.auth.views.LoginView.as_view(template_name="core/login.html"),
        name='login'),
    url(r'^logout$',
        django.contrib.auth.views.LogoutView.as_view(),
        {
            'next_page': '/',
        },
        name='logout'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin', admin.site.urls),

    url(r"^",include("core.urls")),
]+static(settings.STATIC_URL, document_root = settings.STATIC_ROOT)+static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
