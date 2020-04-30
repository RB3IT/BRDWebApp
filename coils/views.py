"""
Definition of views.
"""
## Builtin
import calendar
import datetime
import json

import itertools ## used for assembly the QR's for PDF output
import math ## used for calculating the PDF page output
import base64 ## used for displaying QR PDF in webpage
import io ## Used for QR Printing

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
from inventory import models as inventorymodels

## Third Party
from PIL import Image ## [pillow] Used for QR Printing

## Standard American Month Format for output
MONTHFORMAT = "%m/%d/%Y"

def process(coil):
    """ Coil Serialization method """
    def og_coil(c):
        out = {"pk":c.pk,'size':c.size,'weight':round(c.weight,2), 'width':c.width}
        if c.finished:
            out['stage'] = 'Finished'
            out['date'] = c.finished.strftime(MONTHFORMAT)
        elif c.opened:
            out['stage'] = 'Opened'
            out['date'] = c.opened.strftime(MONTHFORMAT)
        elif c.received:
            out['stage'] = 'Received'
            out['date'] = c.received.strftime(MONTHFORMAT)
        else:
            out['stage'] = "Unknown"
            out['date'] = "N/A"
        return out
    if isinstance(coil,models.SteelCoil):
        out = og_coil(coil)
    else:
        out = {"coil":og_coil(coil.coil)}
        out['width'] = coil.width
        out['weight'] = coil.weight
        out['item'] = coil.item.pk
        out['pk'] = coil.pk
    return out

class CoilHome(dviews.TemplateView):
    """ Coil Homepage """
    template_name = "coils/home.html"

@login_required
def coilregistry(request):
    """ Form for registering a new coil """
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = models.SteelCoilForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            ## Check coilcount
            count = request.POST.get("coilcount")
            try:
                count = int(count)
                assert count > 0
            except:
                form.adderror("coilcount", "Invalid Count")
            else:
                coils = [form.save(commit=False) for coil in range(count)]                    
                ## Until they are saved to db, all instances reference the same [instance?]
                ## (It's weird...)
                coils[0].weight /= count
                ## Clear the pk for each coil so that it saves as a new pk
                for coil in coils:
                    coil.pk = None
                    coil.save()
                if count == 1:
                    return dhttp.HttpResponseRedirect(reverse('viewcoil',kwargs = dict(coil=coil.pk)))
                else:
                    return dhttp.HttpResponseRedirect(reverse("outputcoil"))

    # if a GET (or any other method) we'll create a blank form
    else:
        form = models.SteelCoilForm()

    return render(request, 'coils/coilregistry.html' , {'form': form})

@login_required
@decorators.require_GET
def viewcoil(request,coil):
    """ Displays the stats of a coil """

    coilobj = get_object_or_404(models.SteelCoil,pk = coil)
    return render(request,'coils/viewcoil.html', {"coil":coilobj, 'coilqr':f"{reverse('get_coil_qr')}?coil={coil}"})

@decorators.require_GET
def get_coil_qr(request):
    """ Returns the image for the given coil """

    pk = request.GET.get("coil")
    coil = get_object_or_404(models.SteelCoil,pk = pk)
    qr = coil.generate_qr()
    response = dhttp.HttpResponse(content_type= 'image/png')
    qr.png(response, scale = 5)
    return response

class OutputCoils(dviews.TemplateView):
    template_name = "coils/outputcoils.html"

class EditCoil(dviews.TemplateView):
    template_name = "coils/editcoil.html"
    def get_context_data(self,coil = None,errors = None, **kw):
        ## Get payload
        context = super().get_context_data(**kw)
        coil = get_object_or_404(models.SteelCoil,pk = coil)
        context['coil'] = coil
        context['errors'] = errors
        return context


@login_required
def scancoil(request):
    outputdata = {}
    if request.method == "POST":
        data = request.POST
        files = request.FILES
        qrcode = files.get("qrcode","")
        if qrcode:
            coil = models.SteelCoil.decode_qr(qrcode)
            if not coil:
                outputdata['coilerror'] = True
            else:
                return redirect(reverse("viewcoil", args = (coil.pk,)))
    return render(request,"coils/scancoil.html",outputdata)

@decorators.require_GET
@login_required
def get_coil_list(request):
    """ Returns a list of coil data """

    pagesize = 25
    ## We're adding in some ad hoc pagination to this page
    ## We may switch to site-wide pagination at some point

    data = request.GET
    page = data.get("page",0)
    try: page = int(page)
    except:
        return dhttp.HttpResponseBadRequest(f'Invalid page')
    pagestart = data.get("pagestart",None)
    if not pagestart: pagestart = None
    else:
        try:
            pagestart = int(pagestart)
        except:
            return dhttp.HttpResponseBadRequest(f'Invalid pagestart')

    if pagestart:
        coils = models.SteelCoil.objects.filter(pk__lte=pagestart).order_by("-pk","-received")
    else:
        coils = models.SteelCoil.objects.all().order_by("-pk","-received")
        if coils:
            pagestart = coils[0].pk

    start = page*pagesize
    coils = coils[start:start+pagesize]
    if len(coils) < pagesize:
        nextpage = False
    else:
        nextpage = page + 1

    output = list(map(process,coils))
    return dhttp.JsonResponse({"result":"success","coils":output, "pagestart":pagestart, "nextpage":nextpage})

@decorators.require_GET
@login_required
def get_coil_printout(request):
    """ Returns a number of printable pages containing the requested coil ids and their QR Codes """
    data = request.GET
    values = data.get("coils",None)
    if not values:
        return dhttp.HttpResponseBadRequest(f'Invalid Coils')

    try:
        values = json.loads(values)
        if not isinstance(values,list):
            raise ValueError()
        coils = models.SteelCoil.objects.filter(pk__in=values)
        if len(coils) != len(values):
            raise ValueError()
    except:
        return dhttp.HttpResponseBadRequest(f'Invalid Coils')

    sheet = _create_coilprintout(coils)
    sheet.seek(0)
    response = dhttp.HttpResponse(base64.b64encode(sheet.read()), content_type = "application/pdf")
    return response

class CoilStats(dviews.TemplateView):
    template_name = "coils/coilstats.html"
    def get_context_data(self,**kw):
        ## Get payload
        context = super().get_context_data(**kw)
        data = self.request.GET
        coils = data.get("coils",None)
        coils = base64.b64decode(coils)
        coils = json.loads(coils.decode())
        coils = sorted([get_object_or_404(models.SteelCoil,pk = coil) for coil in coils], key = lambda coil: coil.size)
        sizes = {size: {} for size in sorted(list(set(coil.size for coil in coils)))}
        for size,results in sizes.items():
            scoils = [coil for coil in coils if coil.size == size]
            results['coils'] = scoils
            results['count'] = len(scoils)
            results['total_weight'] = sum([coil.weight for coil in scoils])
        context['sizes'] = sizes
        return context

@decorators.require_POST
@login_required
@csrf.csrf_exempt
def post_coilstatus(request):
    """ Flags the coil's status """
    data = request.POST
    try:
        coil = data.get("coil",None)
        coil = models.SteelCoil.objects.get(pk = coil)
        state = data.get("state",None)
        assert state.lower() in ['open','finish']
    except:
        return dhttp.HttpResponseBadRequest(f'Invalid Coil or State')

    if state.lower() == "open":
        coil.opened = timezone.now()
        output = coil.opened
    elif state.lower() == "finish":
        coil.finished = timezone.now()
        output = coil.finished
    coil.save()
    return dhttp.JsonResponse({"result":"success","date":output})

@decorators.require_POST
@login_required
@csrf.csrf_exempt
def post_coilupdate(request):
    """ Flags the coil's status """
    data = request.POST
    errors = None
    coil = data.get("pk",None)
    coil = models.SteelCoil.objects.filter(pk = coil).first()
    if not coil:
       errors = f"No Such coil {pk}"
       return dhttp.JsonResponse({"result":"failure","errors":errors})
    else:
        errors = []
        size = data.get("size",None)
        try: size = float(size)
        except: pass
        if isinstance(size, (int,float)) and size > 0:
            coil.size = size
        elif not size is None:
            errors.append("size")
        weight = data.get("weight",None)
        try: weight = float(weight)
        except: pass
        if isinstance(weight,(int,float)) and weight > 0:
            coil.weight = weight
        elif not weight is None:
            errors.append("weight")
        width = data.get("width",None)
        try: width = float(width)
        except: pass
        if isinstance(width,(int,float)) and width > 0:
            coil.width = width
        elif not width is None:
            errors.append("width")
        notes = data.get("notes",None)
        if isinstance(notes, str):
            coil.notes = notes
        elif not notes is None:
            errors.append("notes")
    if not errors:
        coil.save()
        return dhttp.JsonResponse({"result":"success"})

    errors = f"The following fields failed to update: {', '.join(errors)}"
    return dhttp.JsonResponse({"result":"failure","errors":errors})

def _create_coilprintout(coils):
    """ Takes a list of coils and returns an Image object that represents a """
    """
    Notes:

    Pagesize = 8.5 x 11
    Margins = 1
    Result = 7.5 x 10
    Margin between images = 1
    1-dot-per-pixel
    If 300 DPI target:
    Imagesize = 300 DPI/Pixels x [7.5,10] == 2250 x 3000 pixels
    Margin between images = 150 Pixels (.5 inch x 300 DPI/Pixels)

    >>>>
    Example (current setup)

    If Target Size of 2 Inches
    QR Image = 600 x 600 Pixels
    600x+150(x-1) = [2250,3000]
    So 3 Wide by 4 Tall
    (600*3 + 150*(3-1) = 2100 [150px (.5 inch) Lost Space])
    (600*4 + 150*(4-1) = 2850 [150px (.5 inch) Lost Space])

    Should have 2 QR Codes per Coil (in case one is not visible),
    so we can get 3 coils per page

    >>>>>
    The whitespace around the qrcode (quiet_zone) is currently set to default: 4 modules
    """
    ## Inches
    pi = page_in_inches = dict(
        dpi = 300,
        pageheight = 11,
        pagewidth = 8.5,
        pagemargin = 1,
        qrheight = 2,
        qrmargin = .5,
    )
    pi['width'] = pi['pagewidth'] - pi['pagemargin']
    pi['height'] = pi['pageheight'] - pi['pagemargin']

    ## Pixels
    """ TODO:
            The QR Code is currently the correct size _with_ whitespace.
            This size is actually 1-1/2 inches (instead of the 2 inches cited
            in {pi}). Removing the whitespace not only requires reworking of
            the scale, but also of the methodology by which the coil ID text is
            added to the image (it is currently placed within the whitespace
            and is manually sized: it sizing, likewise, needs to be automated).
    """
    qr = dict(
        height = pi['qrheight'] * pi['dpi'],
        margin = pi['qrmargin'] * pi['dpi'],
        scale = 20, ## TODO: automate this
        quiet_zone = 4, ## Whitespace around qrcode
    )
    qr['lineheight'] = qr['height']+qr['margin']

    pp = page_in_pixels = dict(
        width = int(pi['width'] * pi['dpi']),
        height = int(pi['height'] * pi['dpi']),
    )

    def getpage(mode = None):
        ## Default is RGBA
        if not mode:
            mode = "RGBA"
            channels = (255,255,255,0)
        elif mode == "RGB":
            channels = (255,255,255)
        return Image.new(mode,(pp['width'],pp['height']),channels)

    ## pp.pagewidth[ or pp.pageheight ] = qrheight * count + qrmargin * (count-1)
    ## pw = qh * c + qm * c - qm
    ## pw + qm = qh * c + qm * c
    ## pw + qm = c (qh + qm)
    ## pw + qm
    ## ------- = c
    ## qh + qm

    coilimgs = [coil.qroutput(scale=qr['scale'],quiet_zone=qr['quiet_zone']) for coil in coils]

    ## Copies was used originally when qr codes were considered for inside the coil
    copies = 1
    coilimgs = list(itertools.chain.from_iterable([[coil for x in range(copies)] for coil in coilimgs]))

    countwidth = int( (pp['width'] + qr['margin']) / (qr['height'] + qr['margin']) )
    countheight = int( (pp['height'] + qr['margin']) / (qr['height'] + qr['margin']) )
    totalcount = countwidth * countheight
    pagecount = math.ceil(len(coilimgs) / totalcount)

    pages = []
    for pnum in range(pagecount):
        page = getpage()
        coils = coilimgs[pnum*totalcount:pnum*totalcount+totalcount]
        for ind,coil in enumerate(coils):
            xi = ind % countwidth
            yi = ind // countwidth
            x = int(xi * (qr['height']+qr['margin']))
            y = int(yi * (qr['height']+qr['margin']))
            page.paste(coil,(x,y))
        ## PDF's can't handle Transparency, so need to flatten
        ## (We have transparency to allow for leeway in placement)
        newpage = getpage("RGB")
        ## masking is the Page's Alpha channel (index 3)
        newpage.paste(page, mask = page.split()[3])
        pages.append(newpage)

    firstpage,pages = pages[0],pages[1:]
    output = io.BytesIO()
    firstpage.save(output,"PDF",append_images = pages, save_all = True)
    ## Be kind, Rewind
    output.seek(0)
    return output

@decorators.require_GET
@login_required
def get_coils(request):
    """ Returns stats for the current (unfinished) coils """
    data = request.GET
    size = data.get("size")
    kw = {}
    if size in ("5.28","5.34"):
        kw['size'] = float(size)
    coils = [process(coil) for coil in models.SteelCoil.objects.filter(finished = None,**kw).order_by("-pk","-received")]
    return dhttp.JsonResponse({"success":True,"coils":coils})


@decorators.require_GET
@login_required
def get_inventory_coils(request):
    """ Returns the coils associated with the given inventory item """
    data = request.GET
    itemid = data.get("item")
    item = get_object_or_404(inventorymodels.Inventory,pk = itemid)
    coils = models.InventoryCoil.objects.filter(item = item)
    return dhttp.JsonResponse({"success":True,"coils":[process(coil) for coil in coils]})

@decorators.require_POST
@login_required
def post_inventory_coil_width(request):
    """ Updates a coil's width given the InventoryCoil's PK """

    def handleCoil(coilid,width):
        """ Get coil by id and update its width """
        invcoil = get_object_or_404(models.InventoryCoil, pk = coilid)
        width = float(width)
        invcoil.width = width
        invcoil.save()

    data = request.POST
    coilid,width = data.get("coil"),data.get("width")

    """
    Array data comes in for "{arrayname}[{index}]"
    When the element is a dict, this is further flattened to : "{arrayname}[{index}][{key}]"
    Currently, trying to use "request.POST.getlist([various values])" does not work,
    so we're going to have to parse by hand.
    """
    if coilid is None:
        coils = []
        last = True
        i = 0
        ## Parse data
        while last:
            last = None
            coil = data.get(f"coils[{i}][coil]")
            if coil:
                width = data.get(f"coils[{i}][width]")
                last = {"coil":coil,"width":width}
                coils.append(last)
                i+=1

        if not coils or not isinstance(coils,list):
            return dhttp.HttpResponseBadRequest("Invalid query")
        for coil in coils:
            handleCoil(coil.get("coil"),coil.get("width"))
    else:
        handleCoil(coilid,width)

    return dhttp.JsonResponse({"success":True})

@decorators.require_POST
@login_required
def post_new_inventory_coil(request):
    data = request.POST
    itemid,coilid = data.get("item"),data.get("coil")
    item = get_object_or_404(inventorymodels.Inventory,pk = itemid)
    coil = get_object_or_404(models.SteelCoil,pk = coilid)
    if models.InventoryCoil.objects.filter(item = item, coil = coil):
        raise dhttp.Http404("Already Exists")
    invcoil = models.InventoryCoil(item = item, coil = coil, width = coil.width)
    invcoil.save()
    return dhttp.JsonResponse({"success":True, "coil":process(invcoil)})

@decorators.require_http_methods(["GET","DELETE"])
@login_required
def get_inventory_coil(request,coil):
    if request.method == "GET":
        coil = get_object_or_404(models.InventoryCoil,pk = coil)
        return dhttp.JsonResponse({"success":True,"coil":process(coil)})
    else: ## request.method == "DELETE"
        coil = get_object_or_404(models.InventoryCoil,pk = coil)
        coil.delete()
        return dhttp.JsonResponse({"success":True})