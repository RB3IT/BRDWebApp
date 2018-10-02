"""
Definition of urls for BRDWebApp.
"""

from datetime import datetime
from django.conf.urls import url
import django.contrib.auth.views
from django.contrib.auth.decorators import login_required

from . import forms
from . import views

# Uncomment the next lines to enable the admin:
from django.conf.urls import include
from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    url(r"^api/item$",views.item_api),
    url(r"^item$",views.Item.as_view()),
    url(r'^index$',views.Index.as_view()),
    url(r'^export$',views.exportinventories),

    ## Default Landing Page
    url(r"^coils/",include("coils.urls")),
    url(r"^",views.MonthSelect.as_view(), name='inventoryhome'),
]
