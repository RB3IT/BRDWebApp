"""
BRDWebApp.kiosk.urls
Definition of urls for BRDWebApp.
"""

from datetime import datetime
from django.conf.urls import url
import django.contrib.auth.views
from django.contrib.auth.decorators import login_required as base_login_req

from . import views

# Uncomment the next lines to enable the admin:
from django.conf.urls import include
from django.contrib import admin
admin.autodiscover()

## Implementation for this submodule to redirect to kiosk-specific login
login_required = base_login_req(login_url = "kiosklogin")

urlpatterns = [
    
    ## Subs
    url(r"^hardware/", include("kiosk.apps.hardware.urls")),
    url(r"^springs/", include("kiosk.apps.springs.urls")),

    url(r"^$",login_required(views.Home.as_view()), name="kioskhome"),
    url(r"^login$", django.contrib.auth.views.LoginView.as_view(template_name="kiosk/login.html"), name = "kiosklogin"),
    url(r"^logout$", views.logoutview, name = "kiosklogout")
]
