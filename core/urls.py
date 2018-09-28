"""
Definition of urls for BRDWebApp.
"""

from datetime import datetime
from django.urls import path
import django.contrib.auth.views

from . import views

# Uncomment the next lines to enable the admin:
from django.conf.urls import include
from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    ## url(r"^inventory/api/item$",inventory.views.item_api),
    path(r"", views.Home.as_view(), name="home"),
    path(r"api/company", views.API_company)
]
