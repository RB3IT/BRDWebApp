"""
BRDWebApp.kiosk.apps.springs.views
Definition of views.
"""
## Builtin
import calendar
import datetime
import json

## Third Party: Django
from django import http as dhttp
from django.core import serializers
from django.utils import timezone
from django.views import generic as dviews
from django.views.decorators import http as decorators
from django.views.decorators import csrf
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
## from django.contrib.auth.decorators import login_required
from ...urls import login_required

## This Module
from . import models
from inventory import models as InvModels

## Custom Module
from alcustoms import methods as almethods

## Sister Module
from BRDSolution.inventory.constants import DATEFORMAT

class Home(dviews.TemplateView):
    """ 
    """
    template_name = "hardware/home.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


@login_required
@decorators.require_GET
def viewitem(request):
    """ Displays the stats of a coil """
    pk = request.GET.get("item")
    itemobj = get_object_or_404(InvModels.Items,pk = pk)
    today = datetime.datetime.today()
    thismonth = today.replace(day = 1)
    lastday = thismonth - datetime.timedelta(days = 1)
    lastmonth = lastday.replace(day = 1)
    return render(request,"hardware/item.html", {"item":itemobj, "thismonth": thismonth.strftime(DATEFORMAT), "lastmonth": lastmonth.strftime(DATEFORMAT)})

