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
    url(r'^springregistry',views.springregistry, name = "springregistry"),
    url(r'^editspring/(?P<spring>\d+)', views.EditSpring.as_view(), name="editspring"),
    url(r'^output',login_required(views.OutputSprings.as_view()), name = 'outputspring'),
    url(r'^(?P<spring>\d+)',views.viewspring, name = 'viewspring'),
    url(r'^getStats',login_required(views.SpringStats.as_view()), name = "stats"),

    url(r'^api/getspringlist', views.get_spring_list, name = 'get_spring_list'),
    url(r'^api/springs', views.get_springs, name='get_springs'),
    url(r'^api/update', views.post_springupdate, name="springupdate"),
    url(r'^api/spring', views.post_springstatus, name="springstate"),
    
    url(r'^',views.SpringHome.as_view(), name = 'springhome'),
]
