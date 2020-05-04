"""
BRDWebApp.kiosk.apps.springs.urls
Definition of urls for BRDWebApp.
"""

from datetime import datetime
from django.conf.urls import url
import django.contrib.auth.views
#from django.contrib.auth.decorators import login_required
from ...urls import login_required

from . import views

# Uncomment the next lines to enable the admin:
from django.conf.urls import include
from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    url(r"^$",login_required(views.Home.as_view()), name="kioskhardwarehome"),
    url(r"^items$",views.viewitem, name="kioskhardwareitem"),
        
]
