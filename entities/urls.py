"""
Definition of urls for BRDWebApp.entities
"""

from django.urls import path
import django.contrib.auth.views

from . import views

# Uncomment the next lines to enable the admin:
from django.conf.urls import include
from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    path(r"api/company", views.API_company)
]
