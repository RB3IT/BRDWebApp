## Backend
from django import http as dhttp
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core import serializers, paginator
from django.db import transaction
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
import django.utils.html as dhtml
from django.views import generic as dviews
from django.views.decorators import http as decorators

## This Module
from entities import models as entitymodels
from . import models, search
from . import ordervalidation as oval
from . import io as dio

## Sister Module
from NewDadsDoor import calculations, classes, methods, sketches, pipecalculations

## Builtin
import collections
import functools
import itertools
import json
import math

## Custom Module
from alcustoms.methods import nestedempty
from alcustoms import measurement

DATEFORMAT = '%d/%m/%Y'
DATEINPUTFORMAT = '%m-%d-%Y'
PAGINATION_SIZE = 25

class ValidationException(Exception): pass

def getspringoptions():
    """ Dict of Spring Lookup Options """
    gauges = list(classes.WIREINDEX)
    ods = classes.SPRINGOD
    cycles = list(classes.CYCLES)
    ## Input's Datalist will not show items that cannot be entered manually
    ## This means that the step attribute precision has to be small enough
    ## that any of the values in gauges/ods can be achieved using the step arrows
    ##     len()-1 to remove decimal point
    ##     max()-1 to ignore first power of 10
    springprecision = 1/10**(max([len(str(gauge))-1 for gauge in gauges]) - 1)
    odprecision = 1/10**(max([len(str(od))-1 for od in ods]) - 1)

    return dict(wiregauges = gauges, ods = ods, springprecision = springprecision, odprecision = odprecision, cycles = cycles)

def generate_door(clearopening_width,clearopening_height,slattype,castendlocks):
    if castendlocks == "true":
        endlocks = "CAST IRON"
    else:
        endlocks = "STAMPED STEEL"

    return methods.basic_torsion_door(clearopening_width, clearopening_height, slat = slattype, endlocks = endlocks)

class Home(LoginRequiredMixin,dviews.TemplateView):
    """ Home View """
    template_name = "doors/index.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

@login_required
@decorators.require_http_methods(["GET","POST"])
def order(request):
    """ Landing and validation for Job Creation """
    data = getspringoptions()
    #if request.method == 'POST':
    #    form = dict(request.POST)
    #    if form.get("orderid"):
    #        obj = models.Order.objects.get(pk = form.get("orderid")[0])
    #        if not obj: return  render(request,"doors/order.html",data)
    #        data = {key:obj.attr(key) for key in JOBVALIDKEYS}
    #    else:
    #        data = {key:"" for key in JOBVALIDKEYS}
    #    for key in JOBVALIDKEYS:
    #        if form.get(key): data[key] = form[key]
    #    data = cleanjobdata(data)
    #else:
    orderid = request.GET.get("orderid")
    error = False
    form = dict()
    if orderid:
        try:
            order = models.Order.objects.filter(pk = int(orderid)).first()
            assert order
        except Exception as e:
            error = "Invalid Order"
        else:
            form = order.to_form()
            form['orderid'] = orderid
    data['form'] = form
    data['error'] = error
    return render(request,"doors/order.html",data)

@login_required
@decorators.require_GET
def API_orderinfo(request):
    """ Shows all components of a given order """
    if request.method == 'GET':
        orderid = request.GET['orderid']
        if not orderid:
            return dhttp.HttpResponseBadRequest("Invalid Order")
        order = models.Order.objects.filter(pk = orderid).first()
        if not order: return dhttp.HttpResponseBadRequest("Invalid Order")
        doors = []
        for door in models.Door.objects.filter(order = orderid):
            doorout = dio.to_dict(door)
            components = []
            for obj in [models.BottomBar,models.CustomAccessory,
                        models.Facia,models.FeederSlat,models.GearCover,models.Hood,
                        models.MotorCover,models.Pipe,models.Slats,models.Tracks]:
                res = [dio.to_dict(res) for res in obj.objects.filter(door = door)]
                for r in res: r['type'] = obj.__name__
                components.extend(res)
            doorout['components'] = components
            doors.append(doorout)
        data = {"success":True,"orderid":orderid,"doors":doors}
        return dhttp.JsonResponse(data)

@login_required
@decorators.require_GET
def API_orderpart(request):
    """ Shows all components of a given order """
    if request.method == 'GET':
        doorid,pk,kind = request.GET.get("doorid"),request.GET.get('id'),request.GET.get("type")
        if doorid is None or pk is None: return dhttp.HttpResponseBadRequest("Invalid Query") 
        lookup = {
            "pipe": models.Pipe,
            "tracks": models.Tracks,
            "slats": models.Slats,
            "bottombar": models.BottomBar,
            "accessory": models.Accessory,
            "accessorybrackets": models.AccessoryBrackets,
            "customaccessory": models.CustomAccessory,
            "facia": models.Facia,
            "feederslat": models.FeederSlat,
            "gearcover": models.GearCover,
            "hood": models.Hood,
            "motorcover": models.MotorCover
            }
        model = lookup.get(kind)
        if not model:
            return dhttp.HttpResponseBadRequest("Invalid Query") 
        door = models.Door.objects.filter(pk = doorid).first()
        obj = model.objects.filter(pk = pk).first()
        if not door or not obj:
            return dhttp.HttpResponseBadRequest("Invalid Query") 
        ## TODO: Validate Door > Obj
        out = dio.cleanoutput(obj,door)
        return dhttp.HttpResponse(json.dumps(out), content_type="application/json")

@login_required
@decorators.require_POST
def ordervalidation(request):
    """ Landing point for order entry.

    Accepts POST only.
    Accepts a json describing the order */in its entirety/* (any omitted information
    will result- in the case of a successful POST- 
    """
    if request.method == 'POST':
        post = json.loads(request.body)
        output,failures = oval.validateorder(post)
        if nestedempty(failures):
            try:
                ## Use atomic transaction to automatically rollback if a discrepency arises
                with transaction.atomic():
                    customer = output['customer']

                    ## Create and Save Items in Order
                    customer,was_created = entitymodels.Company.objects.get_or_create(name = customer)
                    order = output['job']
                    order.customer = customer
                    order.save()

                    for doorobjs in output['doors']:
                        door = doorobjs['door']
                        door.order = order
                        door.save()

                        for component in doorobjs['components']:
                            ## Some components have subcomponents, so they are organized in a dict
                            if isinstance(component,dict):
                                comp = component['object']
                                comp.door = door
                                if isinstance(comp,models.Slats):
                                    endlocks = component['endlocks']
                                    if endlocks:
                                        endlocks.save()
                                        comp.endlocks = endlocks
                                    comp.save()
                                elif isinstance(comp,models.Tracks):
                                    brackets = component['brackets']
                                    if brackets:
                                        brackets.save()
                                        comp.brackets = brackets
                                    comp.save()
                                elif isinstance(comp,models.Pipe):
                                    comp.save()
                            
                                    for spring in component['springs']:
                                        if isinstance(spring,models.Spring):
                                            spring.pipe = comp
                                            spring.save()
                                        else:
                                            failures['doors'].append(f"Invalid Objects: {comp}")
                            elif isinstance(component,(models.Hood,models.BottomBar, models.Accessory,models.AccessoryBrackets)):
                                component.door = door
                                component.save()
                            else:
                                failures['doors'].append(f"Invalid Objects: {component}")
                        if not nestedempty(failures):
                            raise ValidationExceptionclean()
            except ValidationException:                pass

            ## We may have added failures, so have to check again
            if nestedempty(failures):
                response = dhttp.JsonResponse({"successs":True,"ordernumber":order.pk})
                return response
            ## Implicit continuation for new failures
        response = dhttp.JsonResponse({"success":False,"results":failures})
        response.status_code = 400
        return response
    return dhttp.HttpResponseNotAllowed(["POST",])

@login_required
@decorators.require_GET
def orderoverview(request, orderid = None):
    template = "doors/order_overview.html"
    if not request.method == "GET":
        return dhttp.HttpResponseNotAllowed(["GET",])
    if orderid is None:
        return dhttp.HttpResponseBadRequest("Invalid Order ID")
    
    order = models.Order.objects.filter(orderid=orderid)
    if not order:
        return dhttp.HttpResponseBadRequest("Invalid Order ID")

    order = order[0]
    data = json.loads(serializers.serialize("json",[order,]))[0]
    data['fields']['customer'] = order.customer.name
    data['doors'] = list()
    doors = models.Door.objects.filter(order = order)
    for door in doors:        
        output = {"door":door.name,
                  "id": door.pk,
                  "width":measurement.minimizemeasurement(measurement.tomeasurement(door.open_width)),
                  "height":measurement.minimizemeasurement(measurement.tomeasurement(door.open_height)),
                  "hand":door.hand,"components":{"slats":[],"hood":[],"bottombar":[],"tracks":[],"pipe":[],"accessories":[]}}
        components = output['components']
        for pipe in models.Pipe.objects.filter(door = door):
            out = dio.cleanoutput(pipe,door)
            comp = {"id": pipe.pk, "pipediameter":out['pipediameter'],"shaftdiameter":out['shaftdiameter'],"springs":out['springs']}
            components['pipe'].append(comp)
        for hood in models.Hood.objects.filter(door = door):
            out = dio.cleanoutput(hood,door)            
            comp = {"id": out['pk'], "custom": out['custom'],"baffle":out['baffle']}
            components['hood'].append(comp)
        for tracks in models.Tracks.objects.filter(door = door):
            out = dio.cleanoutput(tracks,door)
            comp = {"id": out['pk'], "brackets":{"hand":out['hand']}, "standard":out['standard'], "weatherstripping":out['weatherstripping']}
            components['tracks'].append(comp)
        for slats in models.Slats.objects.filter(door = door):
            out = dio.cleanoutput(slats,door)
            comp = {"id": out['pk'], "slat_type":out['slat_type'], "quantity":out['quantity']}
            components['slats'].append(comp)
        for bottombar in models.BottomBar.objects.filter(door = door):
            out = dio.cleanoutput(bottombar,door)
            comp = {"id": out['pk'], "slat_type":out['slat_type'],"angle":out['angle'],"bottom_rubber":out['bottom_rubber'],"slope":out['slope']}
            components['bottombar'].append(comp)
        for accessorytype in models.ACCESSORYLIST:
            names = []
            for accessory in accessorytype.objects.filter(door = door):
                out = dio.cleanoutput(accessory,door)
                if out.get("kind") is not None:
                    names.append({"id":out['pk'], "name":out['kind']})
                else:
                    names.append({"id":out['pk'], "name":accessory.__class__.__name__})
        if names:
            components['accessories'].extend(names)                
        data['doors'].append(output)
    data = {"order":data}
    return render(request,template,data)

def outputcomponents(door):
    """ This function is used for order?orderid= queries and is used to output the required information to populate that edit order page """
    output = list()
    ## Pipe> auto > Pipe Dia, Pipe Length, Shaft Size > Shaft Length, cycles
    ## >>>>> Spring > type , Spring OD , Wire Dia , Stretch
    for pipe in models.Pipe.objects.filter(door = door):
        out = dict(type="pipe")
        out["pipediameter"],out["pipelength"],out["shaftdiameter"],out["shaftlength"],out["cycles"] = pipe.pipediameter,pipe.pipelength,pipe.shaftdiameter,pipe.shaftlength,pipe.cycles
        out['auto'] = not any([pipe.pipediameter,pipe.pipelength,pipe.shaftdiameter,pipe.shaftlength])
        o = out["springs"] = list()
        #for spring in models.Spring.objects.filter()
        output.append(out)

    ## Tracks > Weatherstripping, Wall Angle [auto], Guide [auto], Custom Guide Holes
    ## >>>>> Brackets > Auto > Bracket Size, Drive Side
    ## Hood > Baffle, Style > Custom Desciption
    ## Slats > Slat Type, Face, Assembly, Endlocks > Continuous, Length [auto], Quantity [auto]
    ## Bottom Bar > Face, Type, Length [auto], Angle, Rubber > Custom Description, Slope > Long Side, Height
    ## Accessories
    return output

@login_required
@decorators.require_GET
def springsetter(request,doorid = None):
    """ Displays various spring options for a given door """
    template = "doors/springsetter.html"
    if request.method != "GET":
        return dhttp.HttpResponseNotAllowed(["GET",])
    if not doorid:
        data = dict()
        return render(request,template,data)
    
    door = models.Door.objects.filter(doorid=doorid).first()
    if not door:
        return dhttp.HttpResponseBadRequest("Invalid Door ID")

    doorinstance = dio.to_doorinstance(door)
    oval.checkdefaults(doorinstance)

    data = getspringoptions()
    data.update(dict(doorid = None, name = None, cyclerating = None, pipesizes = None, weightopen = None, weightclosed = None))
    data['doorid'] = doorid
    data['name'] = door.name
    data['cyclerating'] = doorinstance.pipe.cycles
    data['pipesizes'] = [(pipe,stats['radius']+stats['barrelringsize']) for pipe,stats in classes.PIPESIZES.items()]
    if doorinstance.curtain.slatsections():
        data['weightopen'],data['weightclosed'] = doorinstance.curtain.weight_open,doorinstance.curtain.weight_closed
    if doorinstance.pipe.assembly.sockets:
        data['assembly'] = dio.serialize_assembly(doorinstance.pipe.assembly)
    return render(request,template,data)


@login_required
@decorators.require_GET
def API_assemblies(request):
    """ API Output:

        [                       ## List of Assemblies
            {
                name:"",
                castings: [     ## List of Castings
                    {}, ...     ## List of Springs
                ], ...
            }, ...
        ]
    """
    data = request.GET
    doorid = data.get("doorid")
    if doorid:
        door = models.Door.objects.filter(doorid=doorid).first()
        if not door:
            return dhttp.HttpResponseBadRequest("Invalid Door ID")
        doorinstance = dio.to_doorinstance(door)
    else:
        clearopening_width, clearopening_height = data.get("clearopening_width"), data.get("clearopening_height")
        slattype, castendlocks = data.get("slattype"), data.get("castendlocks")
        try: doorinstance = generate_door(clearopening_width, clearopening_height, slattype, castendlocks)
        except:
            return dhttp.HttpResponseBadRequest("Invalid Door Arguments")

    if not doorinstance:
        return dhttp.HttpResponseBadRequest("Invalid Door")

    pipe = data.get("pipe")
    if pipe:
        doorinstance.pipe.shell =pipe
    if not doorinstance.pipe.shell:
        return dhttp.HttpResponseBadRequest("Invalid Pipe")

    oval.checkdefaults(doorinstance)
    #oval._set_slats(doorinstance)

    assemblies = pipecalculations.generate_all_assemblies(doorinstance.torqueperturn, doorinstance.totalturns, pipe = doorinstance.pipe)
    output= []
    ## index is used for generically naming Assemblies:
    ## i.e.- "1-Spring Assembly", "1-Spring Assembly - 2", "2-Spring Assembly", etc
    index = collections.defaultdict(int)

    for assembly in assemblies:
        i = sum(len(casting.springs) for casting in assembly.sockets)
        out = dio.serialize_assembly(assembly)
        if index[i] == 1: count = ""
        else: count = f" - {index[i]}"
        index[i] += 1
        out['name'] = f"{i}-Spring Assembly{count}"
        output.append(out)
    return dhttp.JsonResponse({"success":True,"results":{'assemblies':output} })

@login_required
@decorators.require_GET
def API_turns(request):
    data = request.GET
    doorid = data.get("doorid")
    door = None
    if doorid is None or doorid == "":
        height,slat,pipe = data.get("height"),data.get("slat"),data.get("pipe")
        torque_open, torque_closed = data.get("requiredtorque_open","requiredtorque_closed")
        try: height = measurement.Imperial(height)
        except: height = None
        try: slat = classes.Slat.parsetype(slat)
        except: slat = None
        try: pipe = constants.PIPESIZE[int(pipe)]
        except: pipe = None
        try: torque_open = float(torque_open)
        except: torque_open = None
        try: torque_closed = float(torque_closed)
        except: torque_closed = None
        if not (height and slat and pipe and torque_open and torque_closed):
            return dhttp.HttpResponseBadRequest("Invalid Request")
        
        turnstoraise = calculations.door_turnstoraise(height, pipe['radius'] + pipe['barrelringsize'], slat.increaseradius)
        torqueperturn = calculations.pipe_torqueperturn(torque_closed, torque_open, turnstoraise)
        preturns = calculations.pipe_preturns(torque_open, torqueperturn)
        turns = calculations.pipe_totalturns(turnstoraise, preturns)

        return dhttp.JsonResponse({"success":True,"results":{"turns":turns,"turnstoraise":turnstoraise,"preturns":preturns}})

    else:
        door = models.Door.objects.filter(doorid=doorid).first()
        if not door:
            return dhttp.HttpResponseBadRequest("Invalid Door ID")
    
        doorinstance = dio.to_doorinstance(door)
        pipe = data.get("pipe")
        if not pipe:
            if not doorinstance.pipe.shell:
                return dhttp.HttpResponseBadRequest("Door requires Pipe Size")
        else:
            doorinstance.pipe.shell = pipe

        oval.checkdefaults(doorinstance)
        #oval._set_slats(doorinstance)
        return dhttp.JsonResponse({"success":True,"results":{"turns":doorinstance.totalturns,"turnstoraise":doorinstance.turnstoraise,"preturns":doorinstance.preturns}})

@login_required
@decorators.require_GET
def API_torque(request):
    data = request.GET
    doorid = data.get("doorid")
    if doorid:
        door = models.Door.objects.filter(doorid=doorid).first()
        if not door:
            return dhttp.HttpResponseBadRequest("Invalid Door ID")
        doorinstance = dio.to_doorinstance(door)
    else:
        slattype, endlocks = data.get("slattype"), data.get("endlocks")
        clearopening_width, clearopening_height = data.get("clearopening_width"),data.get("clearopening_height")
        try:
            doorinstance = methods.basic_torsion_door(width = clearopening_width, height = clearopening_height, slat = slattype, endlocks = endlocks)
        except:
            return dhttp.HttpResponseForbidden("Invalid Request")
    pipe = data.get("pipe")
    if not pipe:
        if not doorinstance.pipe.shell:
            return dhttp.HttpResponseBadRequest("Door requires Pipe Size")
    else:
        doorinstance.pipe.shell = pipe

    oval.checkdefaults(doorinstance)
    #oval._set_slats(doorinstance)
    return dhttp.JsonResponse({"success":True,"results":{"requiredtorqueclosed":doorinstance.requiredtorque_closed,"requiredtorqueopen":doorinstance.requiredtorque_open,"torqueperturn":doorinstance.torqueperturn}})

@login_required
@decorators.require_POST
def API_setsprings(request):
    data = request.POST
    doorid = data.get("doorid")
    if doorid is None:
        return dhttp.HttpResponseServerError("Not Implemented")
    door = models.Door.objects.filter(doorid=doorid).first()
    if not door:
        return dhttp.HttpResponseBadRequest("Invalid Door ID")
    
    pipeobj = models.Pipe.objects.filter(door = door).first()
    pipesize = data.get("pipe")
    if not pipesize:
        if not pipeobj or not pipeobj.pipediameter:
            return dhttp.HttpResponseBadRequest("Door requires Pipe Size")
        pipesize = pipeobj.pipediameter
    else:
        pipeobj.pipediameter = pipesize

    assembly = data.get("assembly")
    if assembly:
        assembly = json.loads(assembly)
        castings = assembly.get("castings", False)
    if not assembly or not castings:
        return dhttp.JsonResponse({"success":False,"reason":"nocastings"})
    
    doorinstance = dio.to_doorinstance(door)
    doorinstance.pipe.shell = pipesize

    oval.checkdefaults(doorinstance)
    #oval._set_slats(doorinstance)
    
    assemblyinstance = doorinstance.pipe.assembly
    assemblyinstance.clear()
    for casting in castings:
        castingobj = classes.Socket()
        for spring in casting:
            springobj = classes.Spring(wire = float(spring['gauge']), od = float(spring['od']))
            springobj.coils = float(spring['coils'])
            castingobj.addspring(springobj)
        assemblyinstance.addsocket(castingobj)

    if not doorinstance.validatepipeassembly():
        return dhttp.JsonResponse({"success":False,"reason":"badcastings"})

    ## Remove previous springs
    models.Spring.objects.filter(pipe = pipeobj).delete()

    ## Save Springs
    for c,casting in enumerate(assemblyinstance.sockets):
        for i,spring in enumerate(casting.springs):
            models.Spring(pipe = pipeobj, spring_type = models.Spring.TYPE[i][0],
                          outer_diameter = spring.od, wire_diameter = spring.wirediameter,
                          uncoiledlength= spring.uncoiledlength, casting = c).save()

    orderid = door.order.pk
    return dhttp.JsonResponse({"success":True,"target": reverse("orderoverview",args = (orderid,))})

class Search(LoginRequiredMixin,dviews.TemplateView):
    """ Order Search View """
    template_name = "doors/search.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        req = self.request.GET
        query = req.get("q")
        if query:
            query = query.strip()
        context['q'] = query

        if query:
            results = search.parse(query)
        else:
            results = models.Order.objects.filter(_delete_flag = False)
        page = req.get("page",1)
        try: page = int(page)
        except: pass
        pagin = paginator.Paginator(results,PAGINATION_SIZE)
        try:
            results = pagin.get_page(page)
        except:
            page = 1
            results = pagin.get_page(page)
        context['orders'] = results
        return context

@login_required
@decorators.require_http_methods(["GET",])
def deleteorder(req,orderid):
    order = get_object_or_404(models.Order,pk = orderid)
    order._delete_flag = True
    order.save()
    return redirect("search")

@login_required
@decorators.require_GET
def sketchoverview(request,doorid):
    template = "doors/sketches.html"
    get_object_or_404(models.Door, pk = doorid)
    data = {"doorid":doorid}
    return render(request,template,data)

@login_required
@decorators.require_GET
def API_sketch(request):
    data = request.GET
    doorid = data.get("doorid")
    door = get_object_or_404(models.Door, pk = doorid)
    doorinstance = dio.to_doorinstance(door)
    output = sketches.shop_drawing(doorinstance, door.order)
    return dhttp.JsonResponse({"success":True,"sketch": output})

DOORVALIDSTATS = ["turnstoraise","totalturns","preturns","hangingweight_closed","hangingweight_open","torqueperturn","requiredtorque_closed","requiredtorque_open"]
PIPEVALIDSTATS = ["shell",]
@login_required
@decorators.require_http_methods(["GET",])
def API_stats(req,*args, **kwargs):
    q = req.GET
    slattype,castendlocks = q.get("slattype"), q.get("castendlocks")
    clearopening_width, clearopening_height = q.get("clearopening_width"), q.get("clearopening_height")
    query = q.get("query","")
    doorq,pipeq = [],[]

    for qu in query.split(","):
        val = qu.split(".")
        name = ""
        if len(val) > 1: name,val = val
        else: val = val[0]
        if name == "pipe":
            if val in PIPEVALIDSTATS: pipeq.append(val)
        elif not name:
            if val in DOORVALIDSTATS: doorq.append(val)


    if not doorq+pipeq: return dhttp.JsonResponse({"success":True,"door": {}})

    door = generate_door(clearopening_width, clearopening_height, slattype, castendlocks)
    output = {}

    for att in doorq:
        output[att] = getattr(door,att)
    if pipeq:
        output['pipe'] = {}
        for att in pipeq:
            output['pipe'][att] = getattr(door.pipe,att)


    return dhttp.JsonResponse({"success":True,"door": output})