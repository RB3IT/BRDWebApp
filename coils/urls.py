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
    url(r'^output',login_required(views.OutputCoils.as_view()), name = 'outputcoil'),
    url(r'^scancoil',views.scancoil, name = 'scancoil'),
    url(r'^(?P<coil>\d+)',views.viewcoil, name = 'viewcoil'),

    url(r'^api/getcoillist', views.get_coil_list, name = 'get_coil_list'),
    url(r'^api/coilqr',views.get_coil_qr, name = 'get_coil_qr'),
    url(r'^api/printcoils',views.get_coil_printout, name = 'get_coil_printout'),
    url(r'^api/coil', views.post_coilstatus, name="coilstate"),
    
    url(r'^',views.CoilHome.as_view(), name = 'coilhome'),
]
