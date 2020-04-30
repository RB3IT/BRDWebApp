"""
Definition of urls for BRDWebApp.
"""

from datetime import datetime
from django.urls import path
import django.contrib.auth.views
from django.views.generic import TemplateView

from . import views

# Uncomment the next lines to enable the admin:
from django.conf.urls import include
from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    path(r"order", views.order, name="order"),
    path(r"order/validate", views.ordervalidation, name = "ordervalidation"),
    path(r"order/delete/<int:orderid>", views.deleteorder, name="deleteorder"),
    path(r"order/api/order", views.API_orderinfo),
    path(r"order/api/component",views.API_orderpart, name = "orderpartapi"),
    path(r"orderinfo/<int:orderid>",views.orderoverview, name="orderoverview"),
    path(r"orderinfo/sketches/<int:doorid>",views.sketchoverview, name = "sketchoverview"),

    path(r"order/api/sketches", views.API_sketch, name = "sketchapi"),

    path(r"search", views.Search.as_view(), name="search"),
    path(r"springs/<int:doorid>",views.springsetter, name = "springsetter"),

    path(r"springs/api/turns",views.API_turns),
    path(r"springs/api/torque",views.API_torque),
    path(r"springs/api/assemblies",views.API_assemblies),
    path(r"springs/api/set", views.API_setsprings),
    path(r"springs/api/all", views.API_stats),

    path(r"doorgen_popup.html", TemplateView.as_view(template_name = "doors/doorgen_popup.html")),
    
    ## Default Landing Page
    path(r"",views.Home.as_view(), name="doorshome"),
]
