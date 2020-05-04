"""
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
from inventory import models as inventorymodels
from NewDadsDoor import constants as nddconstants

## Standard American Month Format for output
MONTHFORMAT = "%m/%d/%Y"

def process(spring):
    """ Spring Serialization method """
    out = {"pk":spring.pk,'size':spring.size,'length':round(spring.length,2)}
    if spring.finished:
        out['stage'] = 'Finished'
        out['date'] = spring.finished.strftime(MONTHFORMAT)
    elif spring.received:
        out['stage'] = 'Received'
        out['date'] = spring.received.strftime(MONTHFORMAT)
    else:
        out['stage'] = "Unknown"
        out['date'] = "N/A"
    return out

class SpringHome(dviews.TemplateView):
    """ Springs Homepage """
    template_name = "springs/home.html"

@login_required
def springregistry(request):
    """ Form for registering a new Spring """
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = models.SpringForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            ## Check springcount
            count = request.POST.get("springcount")
            try:
                count = int(count)
                assert count > 0
            except:
                form.adderror("springcount", "Invalid Count")
            else:
                springs = [form.save(commit=False) for spring in range(count)]                    
                ## Until they are saved to db, all instances reference the same [instance?]
                ## (It's weird...)
                ## Clear the pk for each spring so that it saves as a new pk
                for spring in springs:
                    spring.pk = None
                    spring.save()
                if count == 1:
                    return dhttp.HttpResponseRedirect(reverse('viewspring',kwargs = dict(spring=spring.pk)))
                else:
                    return dhttp.HttpResponseRedirect(reverse("outputspring"))

    # if a GET (or any other method) we'll create a blank form
    else:
        form = models.SpringForm()

    return render(request, 'springs/springregistry.html' , {'form': form, "sizes":list(nddconstants.WIREINDEX)})

@login_required
@decorators.require_http_methods(["GET","POST"])
def viewspring(request,spring):
    """ Displays the stats of a spring """
    if request.method == "GET":
        springobj = get_object_or_404(models.Spring,pk = spring)
        return render(request,'springs/viewspring.html', {"spring":springobj})
    else:
        data = request.POST
        pk,length = data.get('pk'), data.get("length")
        errors = []
        if pk!=spring:
            return dhttp.HttpResponseBadRequest("Invalid spring query")
        try:
            length = float(length)
            assert length > 0
        except:
            errors.append("length")
        springobj = get_object_or_404(models.Spring,pk = spring)
        return render(request,'springs/viewspring.html', {"spring":springobj, "errors":errors})

class OutputSprings(dviews.TemplateView):
    template_name = "springs/outputsprings.html"
    def get_context_data(self,**kw):
        context = super().get_context_data(**kw)
        context['sizes'] = list(nddconstants.WIREINDEX)
        return context

class EditSpring(dviews.TemplateView):
    template_name = "springs/editspring.html"
    def get_context_data(self,spring = None,errors = None, **kw):
        ## Get payload
        context = super().get_context_data(**kw)
        spring = get_object_or_404(models.Spring,pk = spring)
        context['spring'] = spring
        context['errors'] = errors
        context['sizes'] = list(nddconstants.WIREINDEX)
        return context


@decorators.require_GET
@login_required
def get_spring_list(request):
    """ Returns a list of spring data """

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
        springs = models.Spring.objects.filter(pk__lte=pagestart).order_by("-pk","-received")
    else:
        springs = models.Spring.objects.all().order_by("-pk","-received")
        if springs:
            pagestart = springs[0].pk

    start = page*pagesize
    springs = springs[start:start+pagesize]
    if len(springs) < pagesize:
        nextpage = False
    else:
        nextpage = page + 1

    output = list(map(process,springs))
    return dhttp.JsonResponse({"result":"success","springs":output, "pagestart":pagestart, "nextpage":nextpage})

class SpringStats(dviews.TemplateView):
    template_name = "springs/springstats.html"
    def get_context_data(self,**kw):
        ## Get payload
        context = super().get_context_data(**kw)
        data = self.request.GET
        springs = data.get("springs",None)
        springs = base64.b64decode(springs)
        springs = json.loads(springs.decode())
        springs = sorted([get_object_or_404(models.Spring,pk = spring) for spring in springs], key = lambda spring: spring.size)
        sizes = {size: {} for size in sorted(list(set(spring.size for spring in springs)))}
        for size,results in sizes.items():
            s_springs = [spring for spring in springs if spring.size == size]
            results['springs'] = s_springs
            results['count'] = len(s_springs)
            results['total_weight'] = sum([spring.weight for spring in s_springs])
        context['sizes'] = sizes
        return context

@decorators.require_POST
@login_required
@csrf.csrf_exempt
def post_springstatus(request):
    """ Flags the spring's status """
    data = request.POST
    try:
        spring = data.get("spring",None)
        spring = models.Spring.objects.get(pk = spring)
        state = data.get("state",None)
        assert state.lower() in ['finish',]
    except:
        return dhttp.HttpResponseBadRequest(f'Invalid Spring or State')

    if state.lower() == "finish":
        spring.finished = timezone.now()
        output = spring.finished
    spring.save()
    return dhttp.JsonResponse({"result":"success","date":output})

@decorators.require_POST
@login_required
def post_springupdate(request):
    """ Flags the spring's status """
    data = request.POST
    errors = None
    spring = data.get("pk",None)
    spring = models.Spring.objects.filter(pk = spring).first()
    if not spring:
       errors = f"No Such Spring {pk}"
       return dhttp.JsonResponse({"result":"failure","errors":errors})
    else:
        errors = []
        size = data.get("size",None)
        try: size = float(size)
        except: pass
        if isinstance(size, (int,float)) and size > 0:
            spring.size = size
        elif not size is None:
            errors.append("size")
        length = data.get("length",None)
        try: length = float(length)
        except: pass
        if isinstance(length,(int,float)) and length > 0:
            spring.length = length
        elif not length is None:
            errors.append("length")
        notes = data.get("notes",None)
        if isinstance(notes, str):
            spring.notes = notes
        elif not notes is None:
            errors.append("notes")
    if not errors:
        spring.save()
        return dhttp.JsonResponse({"result":"success"})

    errors = f"The following fields failed to update: {', '.join(errors)}"
    return dhttp.JsonResponse({"result":"failure","errors":errors})

@decorators.require_GET
@login_required
def get_springs(request):
    """ Returns stats for the current (unfinished) springs """
    data = request.GET
    size = data.get("size")
    kw = {}
    try:
        size = float(size)
        if size in list(nddconstants.WIREINDEX):
            kw['size'] = size
    except:
        pass
    springs = [process(spring) for spring in models.Spring.objects.filter(finished = None,**kw).order_by("-pk","-received")]
    return dhttp.JsonResponse({"success":True,"springs":springs})