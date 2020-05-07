from django import http as dhttp
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.staticfiles.storage import staticfiles_storage
from django.conf import settings
from django.db.models import F
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import generic as dviews
from django.views.decorators import http as decorators

import base64
import inflect
import io
import json
import xml.etree.ElementTree as ET
import math
import os
import PIL.Image

from . import models
from doors import views as doorviews
from NewDadsDoor import constants

# Create your views here.
class Home(dviews.TemplateView):
    """ Home View """
    template_name = "tools/index.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class BottomBarCalc(dviews.TemplateView):
    """ Bottom Bar Calculator View """
    template_name = "tools/bottombarcalc.html"

class Splitter(dviews.TemplateView):
    """ Bill Splitter View """
    template_name = "tools/billsplitter.html"

class LengthEstimator(dviews.TemplateView):
    """ Length Estimator View """
    template_name = "tools/lengthestimator.html"


class OfficeShoppingList(dviews.TemplateView):
    """ Shopping List for Office Supplies """
    template_name = "tools/officesupplies.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        supplies = []

        if (user := self.request.user).is_authenticated:
            items = models.ShoppingItems.objects.filter(active = True)
            for item in items:
                sitem,created = models.ShoppingListItem.objects.get_or_create(user = user, item = item)
                if created: sitem.save()
                supplies.append(sitem)

        context['supplies'] = supplies
        return context


@decorators.require_http_methods(["GET",])
def update_shoppinglist(request):
    """ Shopping list API """
    r = request.GET

    if not (user := request.user).is_authenticated:
        return dhttp.HttpResponse("Unauthorized", status = 401)

    kind = r.get("type",None)
    name = r.get("name",None)
    value = r.get("value",None)
    if kind == "value":
        try: value = float(value)
        except: value = None
    elif kind == "flag":
        if value not in [True,False]: value = None
    else:
        value == None
    if not name or not isinstance(name,str)\
        or value is None:
        return dhttp.HttpResponseBadRequest("Invalid api")

    item = get_object_or_404(models.ShoppingItems, name = name)
    sitem,created = models.ShoppingListItem.objects.get_or_create(user = user, item = item)

    if kind == "value":
        sitem.quantity = value
    else:
        sitem.reorder_flag = value
    
    sitem.save()

    return dhttp.JsonResponse({"success":True})

@decorators.require_http_methods(["GET",])
def download_shoppinglist(request):
    """ Returns the current Shopping List cached on the server """
    if not (user := request.user):
        return dhttp.HttpResponse("Unauthorized", status = 401)

    file = output_supplies(user)
    response = dhttp.HttpResponse(file, content_type='application/force-download')
    response['Content-Disposition'] = f'attachment; filename="Shopping List.html"'
    return response

with staticfiles_storage.open("tools/shopping/noimage.svg", mode='rb') as f:
    NOIMAGE = base64.b64encode(f.read()).decode("ascii")
del f

def output_supplies(user):
    ## Pluralizer
    p = inflect.engine()
    reorder = models.ShoppingListItem.objects.filter(user = user, item__active = True, quantity__lte = F("item__reorder_quantity")).order_by("item__name")
    
    doc = ET.Element("html")
    head = ET.Element("head")
    doc.append(head)
    charset = ET.Element("meta",attrib={"charset":"UTF-8"})
    head.append(charset)
    style = ET.Element("style")
    head.append(style)
    style.text = """
h1{
    text-align: center;
}
table{
    margin:auto;
}
.noitems{
    color:red;
    font-weight:bold;
    font-size:1.25em;
}
.image{
    max-height: 90px;
    max-width: 90px;
}
.item{
    font-weight:bold;
    padding-right:1em;
}
.quant{
    text-align: right;
}
"""
    body = ET.Element("body")
    doc.append(body)
    header = ET.Element("h1")
    body.append(header)
    header.text = "Shopping List"
    table = ET.Element("table")
    body.append(table)
    if not reorder:
        row = ET.Element("tr")
        table.append(row)

        out = ET.Element("td", attrib={"class":"noitems","colspan":"2"})
        out.text=u"No Items in Shopping List! 😎 Have a Great Day!"
        row.append(out)
    for sitem in reorder:
        row = ET.Element("tr")

        td = ET.Element("td")
        img = ET.Element("img",attrib={"class":"image"})
        try:
            imgdata = base64.b64encode(sitem.item.thumbnail.read()).decode('ascii')
            imgtype = "jpg"
        except:
            imgdata = NOIMAGE
            imgtype = "svg+xml"
        img.attrib['src'] = f"data:image/{imgtype};base64, {imgdata}"
        td.append(img)
        row.append(td)
        
        name = ET.Element("td",attrib={"class":"item"})
        name.text = sitem.item.name
        row.append(name)

        quantcol = ET.Element("td",attrib={"class":"quant"})
        orderquant = math.ceil(sitem.item.max_quantity-sitem.quantity)
        quantcol.text = f"{orderquant} {p.plural(sitem.item.unit,orderquant)}"
        row.append(quantcol)

        table.append(row)

    f = io.StringIO()
    f.write("""<!DOCTYPE html>""")
    ET.ElementTree(doc).write(f,xml_declaration=False,encoding="unicode")
    f.seek(0)
    return f

class SpringsTool(dviews.TemplateView):
    """ Shopping List for Office Supplies """
    template_name = "doors/springsetter.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['doorid'] = None
        context['pipesizes'] = [(pipe,stats['radius']+stats['barrelringsize']) for pipe,stats in constants.PIPESIZES.items()]
        context.update(doorviews.getspringoptions())
        return context