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
    path(r"order", views.order, name="order"),
    path(r"order/validate", views.ordervalidation, name = "ordervalidation"),
    path(r"orderinfo/componentapi",views.orderpart, name = "orderpartapi"),
    path(r"orderinfo/<int:orderid>",views.orderoverview, name="orderoverview"),
    path(r"orderinfo/doorupdate",views.updatedoor,name="doorupdate"),
    path(r"search", views.searchorder, name="search"),
    path(r"springs/<int:doorid>",views.springsetter, name = "springsetter"),
    path(r"springs/api/turns",views.API_turns),
    path(r"springs/api/torque",views.API_torque),
    path(r"springs/api/assemblies",views.API_assemblies),
    path(r"springs/api/set", views.API_setsprings),
    
    ## Default Landing Page
    path(r"",views.Home.as_view(), name="doorshome"),
]
