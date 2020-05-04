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
from django.contrib.auth.decorators import login_required

## This Module
from . import models

## Standard American Month Format for output
MONTHFORMAT = "%m/%d/%Y"

class Home(dviews.TemplateView):
    """ 
    """
    template_name = "springs/home.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context