from django import http as dhttp
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.shortcuts import render
from django.urls import reverse
from django.views import generic as dviews
from django.views.decorators import http as decorators

import base64
import inflect
import json
import xml.etree.ElementTree as ET
import math
import os
import PIL.Image

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


SUPPLYFILE = os.path.join(settings.PROJECT_ROOT , "supplies.json")
SHOPPINGLISTFILE = os.path.join(settings.PROJECT_ROOT , "shoppinglist.html")
SHOPPINGLISTIMGS = os.path.join(settings.MEDIA_ROOT,"shopping")
with open(os.path.join(SHOPPINGLISTIMGS,"no image.svg"),'rb') as f:
    NOIMAGE = base64.b64encode(f.read()).decode("ascii")
del f
def load_supplies():
    """ Loads and returns the local supply file via the json module """
    with open(SUPPLYFILE, 'r') as f:
        supplies = json.load(f)
    for item in supplies['supplies']: item['reorder_quantity'] = float(item['reorder_quantity'])
    return supplies

def save_supplies(supplies):
    """ Saves the supply file via the json module """
    supplies['supplies'] = sorted(supplies['supplies'], key = lambda item: item['name'])
    with open(SUPPLYFILE,'w') as f:
        return json.dump(supplies,f)

def output_supplies():
    ## Pluralizer
    p = inflect.engine()
    supplies = load_supplies()['supplies']
    output = []
    for item in supplies:
        if item['quantity'] <= item['reorder_quantity'] or item['reorder_flag']:
            output.append(item)

    output = sorted(output, key = lambda item: item['name'])
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
    if not output:
        row = ET.Element("tr")
        table.append(row)

        out = ET.Element("td", attrib={"class":"noitems","colspan":"2"})
        out.text=u"No Items in Shopping List! 😎 Have a Great Day!"
        row.append(out)
    for item in output:
        row = ET.Element("tr")

        td = ET.Element("td")
        img = ET.Element("img",attrib={"class":"image"})
        ## .thumbnail files are jpegs, for the record
        imgpath = os.path.join(SHOPPINGLISTIMGS,item['name']+".thumbnail")
        try:
            with open(imgpath,'rb') as f:
                imgdata = base64.b64encode(f.read()).decode('ascii')
            imgtype = "jpg"
        except:
            imgdata = NOIMAGE
            imgtype = "svg+xml"
        img.attrib['src'] = f"data:image/{imgtype};base64, {imgdata}"
        td.append(img)
        row.append(td)
        
        name = ET.Element("td",attrib={"class":"item"})
        name.text = item['name']
        row.append(name)

        quantcol = ET.Element("td",attrib={"class":"quant"})
        orderquant = math.ceil(item['max_quantity']-item['quantity'])
        quantcol.text = f"{orderquant} {p.plural(item['unit'],orderquant)}"
        row.append(quantcol)

        table.append(row)

    with open(SHOPPINGLISTFILE,'w',encoding="utf-8") as f:
        f.write("""<!DOCTYPE html>""")
        ET.ElementTree(doc).write(f,xml_declaration=False,encoding="unicode")

class OfficeShoppingList(dviews.TemplateView):
    """ Shopping List for Office Supplies """
    template_name = "tools/officesupplies.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        supplies = load_supplies()
        context['supplies'] = supplies['supplies']
        return context

   
@decorators.require_http_methods(["GET",])
def update_shoppinglist(request):
    """ Shopping list API """
    r = request.GET

    kind = r.get("type",None)
    name = r.get("name",None)
    value = json.loads(r.get("value",None))
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

    supplies = load_supplies()
    for item in supplies['supplies']:
        if item['name'] == name:
            name = item
            break
    if not isinstance(name,dict):
        return dhttp.HttpResponseBadRequest("Invalid api")

    if kind == "value":
        item['quantity'] = value
    else:
        item['reorder_flag'] = value
    
    save_supplies(supplies)
    output_supplies()
    return dhttp.JsonResponse({"success":True})

@decorators.require_http_methods(["GET",])
def download_shoppinglist(request):
    """ Returns the current Shopping List cached on the server """
    with open(SHOPPINGLISTFILE,'r') as f:
        file = f.read()
    response = dhttp.HttpResponse(file, content_type='application/force-download')
    response['Content-Disposition'] = f'attachment; filename="Shopping List.html"'
    return response


class SpringsTool(dviews.TemplateView):
    """ Shopping List for Office Supplies """
    template_name = "doors/springsetter.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['doorid'] = None
        context['pipesizes'] = [(pipe,stats['radius']+stats['barrelringsize']) for pipe,stats in constants.PIPESIZES.items()]
        context.update(doorviews.getspringoptions())
        return context