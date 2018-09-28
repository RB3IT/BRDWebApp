"""
Definition of views.
"""
## Builtin
import calendar
import datetime
import json

import base64 ## used for displaying QR PDF in webpage
import io ## Used for QR Printing

## Third Party: Django
from django import http as dhttp
from django.core import serializers
from django.views import generic as dviews
from django.views.decorators import http as decorators
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required

## This Module
from . import excelmethods
from . import methods
from . import models
from . import subclasses

## Custom Module
from alcustoms import methods as almethods

## Sister Module
from BRDSolution.inventory.constants import DATEFORMAT

## Third Party
from PIL import Image ## [pillow] Used for QR Printing

def exportinventories(request):
    """ Export to Excel Workbook API Endpoint

    Method: Post
    Requires Authentication
    Payload:
        "end": DATEFORMAT string from year 1900 to 2100; Required
        <Requires One of the Following>
        "ytd": [Any Value]
        "start": DATEFORMAT string from year 1900 to 2100
    end indicates the final Month to include
    ytd is shorthand for January of the same year as end
    start otherwise indicates the first month to include and will return all intermediary months
    """
    ## Requires Post
    if request.method != "POST": return dhttp.HttpResponseNotAllowed(["POST",])
    ## Requires Authentication
    if not request.user.is_authenticated: return dhttp.HttpResponse("Unauthorized",status=401)
    
    ## Get payload
    data = request.POST
    
    ## All data requires end; one of (start,ytd) must be used
    if 'end' not in data or all(key not in data for key in ['start','ytd']):
        return dhttp.HttpResponseBadRequest('missing key')
    
    ## Convert datestrings to datetimes and handle ytd
    try:
        if 'ytd' in data:
            end = datetime.datetime.strptime(data['end'],DATEFORMAT)
            start = methods.getlastdecember(end)
        else:
            start = datetime.datetime.strptime(data['start'],DATEFORMAT)
            end = datetime.datetime.strptime(data['end'],DATEFORMAT)
    ## If Datetimes cannot be converted, Bad Request
    except: return dhttp.HttpResponseBadRequest('bad dates')

    ## Makes sure dates are within range
    if not methods.validatedatetime(start): return dhttp.HttpResponseBadRequest('bad start')
    if not methods.validatedatetime(end): return dhttp.HttpResponseBadRequest('bad end')

    ## Create and serve download
    file = excelmethods.createexceldownload(start,end)
    response = dhttp.HttpResponse(file, content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = f'attachment; filename="Inventory {start.strftime("%m-%Y")} to {end.strftime("%m-%Y")}.xlsx"'
    return response


class Index(dviews.TemplateView):
    """ Inventory View

    A list view of inventory items for a given month with general information available.
    Payload:
        "month": Integer index or Full Month name; Required
        "year": Integer; Required

    If Month/Year is not supplied or invalid, Template will render without records
    """
    template_name = "inventory/inventoryform.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        req = self.request.GET
        month,year = req.get('month'),req.get('year')
        if month and year:
            dt = methods.validatedate(month,year)
            if dt:
                context['month'],context['year'] = dt.month,dt.year
                inventory = methods.getinventorybymonth(dt)
                context['inventorylist']=inventory

                context['nextmonth'] = dict()
                context['prevmonth'] = dict()
                nextmonth = almethods.getfirstofnextmonthdatetime(dt)
                if methods.validatedatetime(nextmonth):
                    context['nextmonth']['month'] = nextmonth.month
                    context['nextmonth']['year'] = nextmonth.year
                prevmonth = almethods.getfirstofpreviousmonthdatetime(dt)
                if methods.validatedatetime(prevmonth):
                    context['prevmonth']['month'] = prevmonth.month
                    context['prevmonth']['year'] = prevmonth.year
        return context

class Item(dviews.TemplateView):
    """ Item View

    The Basic view for an individual item.
    Payload:
        "month": Integer index or Full Month name; Required
        "year": Integer; Required
        "item": itemindex

    If item is not supplied or month and year are invalid/missing,
    then template will be rendered with "No Item".
    """
    template_name = "inventory/itemform.html"
    def get_context_data(self,**kw):
        ## Get payload
        context = super().get_context_data(**kw)
        req = self.request.GET

        ##  Get important data
        month,year,item = req.get('month'), req.get('year'), req.get('item')

        ## Preemptively clear item
        context['item'] = None

        dt = False
        ## Validate month, year
        if month and year:
            dt= methods.validatedate(month=month,year=year)
            if dt: context['month'],context['year'] = dt.month, dt.year
        ## For bad dates, we'll ignore the item request
        if not dt: item = None

        ## Handle item
        if item:

            ## Check for currently set inventory object
            currentinventory = models.Inventory.objects.filter(itemid = item, date = dt)
            ## If none, create an Item object to be the base
            if not currentinventory:
                itemobj = models.Items.objects.filter(itemid = item)
                if itemobj: itemobj = itemobj[0]
            ## Otherwise, take the base item object from the current inventory
            else:
                currentinventory = currentinventory[0]
                itemobj = currentinventory.itemid

            ## If we can make the base, then we can precede
            if itemobj:
                ## Use transporting object
                ## (I'm sure I had a good reason for this at one point...)
                inventoryitem = subclasses.InventoryItem(itemid=itemobj.itemid,itemindex = itemobj.itemindex, date=dt,description=itemobj.description,
                                                         location=itemobj.location, sublocation = itemobj.sublocation, unitsize=itemobj.unitsize,
                                                         notes=itemobj.notes, image = itemobj.image)
                ## Update transport obejct if we have a current inventory
                if currentinventory:
                    inventoryitem.quantity = currentinventory.quantity
                    inventoryitem.usernotes = currentinventory.usernotes
                    inventoryitem.sums = currentinventory.sums
                ## set item
                context['item'] = inventoryitem
                
                items = methods.getincludeditems(dt)


                ## Get previous itemid for navigation
                previd = items.filter(itemindex__lt=inventoryitem.itemindex).order_by('-itemindex')
                if not previd: previd = False
                else: previd = previd[0].itemid

                ## Get next itemid for navigation
                nextid = items.filter(itemindex__gt=inventoryitem.itemindex).order_by('itemindex')
                if not nextid: nextid = False
                else: nextid = nextid[0].itemid

                ## Set navigation ids
                context['previd'] = previd
                context['nextid'] = nextid

            ## If we didn't have a base object, cannot proceed
            else: context['item'] = None

        ## Return Context data to template renderer
        return context




def item_api(request):
    """ API endpoint for updating Inventory Item Attributes

    Currently supports: quantity, sums, usernotes
    """
    ## Ensure only Post
    if request.method != "POST":
        return dhttp.HttpResponseNotAllowed(["POST",])
    ## Check authentication
    if not request.user.is_authenticated:
        return dhttp.HttpResponse("Unauthorized",status=401)

    ## Get POST data
    data = request.POST
    ## Required Keys to update inventory are itemid and date
    if any(key not in data for key in ['itemid','date']):
        return dhttp.HttpResponseBadRequest('missing key')

    itemid,date= data['itemid'], data['date']
    ## Get base item using itemid
    item = models.Items.objects.filter(itemid=itemid)
    ## If invalid itemid
    if not item:
        return dhttp.HttpResponseBadRequest('itemid')
    item = item[0]

    ## Validate date
    try:
        date = datetime.datetime.strptime(date,DATEFORMAT).date()
    except:
        return dhttp.HttpResponseBadRequest('date')

    input = dict()
    ## Each supported attribute has a validator which returns a result or False (for invalid submission)
    for key,validator in [("quantity",item_api_quantity),
                          ("sums",item_api_sums),
                          ("usernotes",item_api_usernotes)]:
        ## Assume False
        success = False
        ## Check if we're updating the key
        if key in data:
            ## Validate submission
            success = validator(item,date,data[key])
            ## If invalid, return BadRequest
            if success is False:
                return dhttp.HttpResponseBadRequest(f'Improperly formatted {key.capitalize()}')
            ## Otherwise, store input data
            input[key] = success

    ## If no attributes were updated (otherwise we would have returned for invalid posts above)
    if not input: return dhttp.JsonResponse({"result":"failure"})

    ## Update Inventory Object
    obj,created=models.Inventory.objects.update_or_create(itemid=item,date=date,defaults=input)
    ## Make sure to save it
    obj.save()
    ## Convert to json so that we can return it with the response
    objserial = serializers.serialize('python',[obj,])[0]['fields']
    ## Respond with success and new, updated object
    return dhttp.JsonResponse({"result":"success","object":objserial})

def item_api_usernotes(item,date, notes):
    """ Validates User-submitted Notes
    
    Notes should be strings
    """
    if not isinstance(notes,str):
        return False
    return notes

def item_api_quantity(item,date, quantity):
    if quantity in ("None",""):
        quantity = None
    if quantity is not None:
        try: quantity = float(quantity)
        except:
            return False
    return quantity

def item_api_sums(item,date, sums):
    if sums in ("None",""):
        sums = None
    if almethods.isiterable(sums):
        try: sums = "\n".join(sums)
        except:
            return False
    if not isinstance(sums,str) and sums is not None:
        return False
    return sums

class MonthSelect(dviews.TemplateView):
    template_name = "inventory/inventorymonthselect.html"