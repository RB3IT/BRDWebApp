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
    path("bbarcalc",views.BottomBarCalc.as_view(), name="bottombarcalc"),
    path("splitter",views.Splitter.as_view(), name = "splittertool"),
    path("lengthestimator",views.LengthEstimator.as_view(), name = "lengthestimator"),
    path("shoppinglist",views.OfficeShoppingList.as_view(), name = "shoppinglist"),
    path("shoppinglist/",views.update_shoppinglist, name = "shoppinglist_api"),

    ## Default Landing Page
    path(r"",views.Home.as_view(), name='toolshome'),
]
