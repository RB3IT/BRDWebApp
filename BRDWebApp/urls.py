"""
Definition of urls for BRDWebApp.
"""

from datetime import datetime
from django.conf.urls import url
import django.contrib.auth.views

from inventory import forms

# Uncomment the next lines to enable the admin:
from django.conf.urls import include
from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    url(r"^inventory/",include("inventory.urls")),
    url(r"^doors/", include("doors.urls")),
    url(r"^tools/", include("tools.urls")),
    url(r'^.*login/$',
        django.contrib.auth.views.login,
        {
            'template_name': 'core/login.html',
            'authentication_form': forms.BootstrapAuthenticationForm,
            'extra_context':
            {
                'title': 'Log in',
                'year': datetime.now().year,
            }
        },
        name='login'),
    url(r'^logout$',
        django.contrib.auth.views.logout,
        {
            'next_page': '/',
        },
        name='logout'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin', admin.site.urls),

    url(r"^",include("core.urls")),
]
