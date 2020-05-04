"""
BRDWebApp.kiosk.models
Definition of models.
"""
## This module
from . import models

## Builtin
import datetime
## Backend
from django.db import models
from django import forms
from django.contrib import admin

from inventory import models as InvModels


## DATABASE FLOWCHART AT: https://drive.google.com/file/d/0BwZSKBgxjIOoZ0w0aVJrb1FPMTQ/view?usp=sharing
## NOTE: Methods inherits from Models, so DON'T IMPORT HERE!

# Create your models here.

## ALL DATES SHOULD BE FIRST-OF-MONTH