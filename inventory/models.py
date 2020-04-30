"""
Definition of models.
"""
## Builtin
import io
import datetime
## Backend
from django.db import models
from django import forms
from django.contrib import admin

## Third Party
## All of these are for QR code reading and writing
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pyzbar import pyzbar
import pyqrcode


## DATABASE FLOWCHART AT: https://drive.google.com/file/d/0BwZSKBgxjIOoZ0w0aVJrb1FPMTQ/view?usp=sharing
## NOTE: Methods inherits from Models, so DON'T IMPORT HERE!

# Create your models here.

## ALL DATES SHOULD BE FIRST-OF-MONTH

class Items(models.Model):
    """ General Item Information
    
    unitsize is the unit of measurement (i.e.- Pounds, Feet, Unit)
    location is the Bay (i.e.- Bristol, Belmont, Pipe Shop)
    sublocation is a distinguished area of the Bay (i.e.- [Bristol] Breaker Area, [Pipe Shop] Hardware Case)
    Photobox is available for image; sublocation picture can be composited or used instead.
    """
    itemid = models.TextField(primary_key=True)
    itemindex = models.FloatField(blank=True, null=True)
    item = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    unitsize = models.TextField(blank=True, null=True)
    location = models.TextField(blank=True, null=True)
    sublocation = models.TextField(blank = True, null = True)
    notes = models.TextField(blank = True, null = True)
    image = models.ImageField(blank = True, null = True, upload_to="inventory\images")

    class Meta: 
        db_table = 'items'

    def __str__(self):
        return self.description

class ItemsAdmin(admin.ModelAdmin):
    list_display = ("itemid","itemindex","description", "location")


class Costs(models.Model):
    """ Cost Lookup Table

    Doing costs individually and dynamically removes need to reassert costs each months.
    """
    itemid = models.ForeignKey('Items', models.DO_NOTHING, db_column='itemid')
    date = models.DateField()
    cost = models.FloatField(blank=True, null = True, default = 0)  # This field type was a guess.
    price = models.FloatField(blank=True, null = True, default = 0)  # This field type was a guess.
    vendor = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'costs'
        unique_together = (('itemid', 'date'),)

    def __str__(self):
        return f"{self.itemid} Cost"

class CostsAdmin(admin.ModelAdmin):
    list_display = ("itemid","date")

class Inventory(models.Model):
    """ Monthly Inventory Count

    What quantity measures depends on Items table.
    """
    itemid = models.ForeignKey('Items', models.DO_NOTHING, db_column='itemid')
    date = models.DateField()
    quantity = models.FloatField(blank=True, null = True, default = 0)  # This field type was a guess.
    usernotes = models.TextField(blank = True, null = True)
    sums = models.TextField(blank = True, null = True)

    class Meta:
        db_table = 'inventory'
        unique_together = (('itemid', 'date'),)

    def __str__(self):
        return f"{self.itemid} Inventory"

class InventoryAdmin(admin.ModelAdmin):
    list_display = ("itemid","date")

class Stock(models.Model):
    """ Whether and When an Item is in Stock """
    itemid = models.ForeignKey("Items", models.DO_NOTHING, db_column = "itemid")
    date = models.DateField(default = datetime.datetime(1900,1,1))
    include = models.NullBooleanField()

    class Meta:
        db_table = "stock"

    def __str__(self):
        return f"{self.itemid} Stock"

class StockAdmin(admin.ModelAdmin):
    list_display = ("itemid","date","include")

class StockWidgets(models.Model):
    """ Stock GUI widgets that are associated with an Inventory Item. """
    itemid = models.ForeignKey("Items", models.DO_NOTHING, db_column = "itemid", null = False, blank = False)
    widget = models.CharField(max_length = 250, null = False, blank = False)

class StockWidgetsAdmin(admin.ModelAdmin):
    list_display = ("itemid","widget")