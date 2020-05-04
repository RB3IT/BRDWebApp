"""
Definition of models.
"""
## This module
from inventory.models import Inventory

## Builtin
import datetime
## Backend
from django.db import models
from django import forms
from django.contrib import admin


## DATABASE FLOWCHART AT: https://drive.google.com/file/d/0BwZSKBgxjIOoZ0w0aVJrb1FPMTQ/view?usp=sharing
## NOTE: Methods inherits from Models, so DON'T IMPORT HERE!

# Create your models here.

class Spring(models.Model):
    """ Registers Springs (with size and length), generating an ID number, and tracks recieved and finished timestamps """
    size = models.FloatField(verbose_name="Size of Spring", null = False, blank = False)
    length = models.FloatField(verbose_name="Length of Spring")
    received = models.DateTimeField(verbose_name = "Received Date", auto_now_add = True)
    finished = models.DateTimeField(verbose_name = "Finished Date", null = True)
    notes = models.TextField()

    @property
    def stage(self):
        if self.finished: return "Finished"
        if self.received: return "Received"

    @property
    def stage_date(self):
        stage = self.stage
        if stage == "Finished": return self.finished
        if stage == "Received": return self.received


class SpringForm(forms.ModelForm):
    """ Spring Entry Form """
    class Meta:
        model = Spring
        fields = ["size","length"]

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get("length"):
            self.add_error("length","No length supplied")

class SpringConsumption(models.Model):
    """ A record of springs that were used """
    spring = models.ForeignKey("Spring", models.DO_NOTHING, blank = False, null = False)
    date = models.DateTimeField(verbose_name = "Date Used", auto_now_add = True)
    length = models.FloatField(verbose_name = "Length Used")