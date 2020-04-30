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
    url(r"^api/item/(?P<itemid>.+?)/(?P<date>\d+-\d+-\d+)", views.inventoryitem_api, name="get_or_create_inventory"),
    url(r"^api/item$",views.item_api, name="inventory_update"),
    url(r"^api/itemlist$", views.itemlist_api, name="api_getitem"),
    url(r"^item$",views.Item.as_view()),
    url(r'^index$',views.Index.as_view()),
    url(r'^export$',views.exportinventories),

    ## Default Landing Page
    url(r"^coils/",include("coils.urls")),
    url(r"^springs/", include("springs.urls")),
    url(r"^$",views.MonthSelect.as_view(), name='inventoryhome'),
]
