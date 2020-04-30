"""
Definition of urls for BRDWebApp.
"""

from datetime import datetime
from django.conf.urls import url
import django.contrib.auth.views
from django.contrib.auth.decorators import login_required

from . import views

# Uncomment the next lines to enable the admin:
from django.conf.urls import include
from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    url(r'^coilregistry',views.coilregistry, name = "coilregistry"),
    url(r'^editcoil/(?P<coil>\d+)', views.EditCoil.as_view(), name="editcoil"),
    url(r'^output',login_required(views.OutputCoils.as_view()), name = 'outputcoil'),
    url(r'^scancoil',views.scancoil, name = 'scancoil'),
    url(r'^(?P<coil>\d+)',views.viewcoil, name = 'viewcoil'),
    url(r'^getStats',login_required(views.CoilStats.as_view()), name = "stats"),

    url(r'^api/getcoillist', views.get_coil_list, name = 'get_coil_list'),
    url(r'^api/coilqr',views.get_coil_qr, name = 'get_coil_qr'),
    url(r'^api/printcoils',views.get_coil_printout, name = 'get_coil_printout'),
    url(r'^api/coils', views.get_coils, name='get_coils'),
    url(r'^api/update', views.post_coilupdate, name="coilupdate"),
    url(r'^api/coil', views.post_coilstatus, name="coilstate"),
    url(r'^api/inventorycoils$', views.get_inventory_coils, name="inventorycoils"),
    url(r'^api/inventorycoils/width', views.post_inventory_coil_width, name = "inventorycoil_update"),
    url(r'^api/inventorycoils/coil', views.post_new_inventory_coil, name="add_inventorycoils"),
    url(r'^api/inventorycoils/(?P<coil>\d+)$', views.get_inventory_coil, name="get_inventorycoil"),
    
    url(r'^',views.CoilHome.as_view(), name = 'coilhome'),
]
