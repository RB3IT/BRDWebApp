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

## Third Party
from PIL import Image ## [pillow] Used for QR Printing

## Standard American Month Format for output
MONTHFORMAT = "%m/%d/%Y"

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
        coils = models.SteelCoil.objects.filter(pk__lte=pagestart).order_by("-pk","-recieved")
    else:
        coils = models.SteelCoil.objects.all().order_by("-pk","-recieved")

    start = page*pagesize
    coils = coils[start:start+pagesize]

    def process(coil):
        out = {"pk":coil.pk,'size':coil.size,'weight':round(coil.weight,2)}
        if coil.finished:
            out['stage'] = 'Finished'
            out['date'] = coil.finished.strftime(MONTHFORMAT)
        elif coil.opened:
            out['stage'] = 'Opened'
            out['date'] = coil.opened.strftime(MONTHFORMAT)
        elif coil.recieved:
            out['stage'] = 'Recieved'
            out['date'] = coil.recieved.strftime(MONTHFORMAT)
        else:
            out['stage'] = "Unknown"
            out['date'] = "N/A"
        return out

    output = list(map(process,coils))
    return dhttp.JsonResponse({"result":"success","coils":output})

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
    print(pages)
    output = io.BytesIO()
    firstpage.save(output,"PDF",append_images = pages, save_all = True)
    ## Be kind, Rewind
    output.seek(0)
    return output