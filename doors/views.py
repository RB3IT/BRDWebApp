## Backend
from django import http as dhttp
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core import serializers
from django.db import transaction
from django.shortcuts import render
from django.urls import reverse
import django.utils.html as dhtml
from django.views import generic as dviews
from django.views.decorators import http as decorators

## This Module
from core import models as coremodels
from . import models
from .ordervalidation import validateorder, JOBVALIDKEYS, to_dict, to_doorinstance, checkdefaults

## Sister Module
from NewDadsDoor import classes, methods

## Builtin
import collections
import datetime
import itertools
import json
import math

## Custom Module
from alcustoms.methods import nestedempty, roundtofraction
from alcustoms import measurement

DATEFORMAT = '%d/%m/%Y'
DATEINPUTFORMAT = '%m-%d-%Y'

class ValidationException(Exception): pass

def getspringoptions():
    """ Dict of Spring Lookup Options """
    gauges = list(classes.WIREINDEX)
    ods = classes.SPRINGOD
    cycles = list(classes.CYCLES)
    ## Input's Datalist will not show items that cannot be entered manuall
    ## This means that the step attribute precision has to be small enough
    ## that any of the values in gauges/ods can be achieved using the step arrows
    ##     len()-1 to remove decimal point
    ##     max()-1 to ignore first power of 10
    springprecision = 1/10**(max([len(str(gauge))-1 for gauge in gauges]) - 1)
    odprecision = 1/10**(max([len(str(od))-1 for od in ods]) - 1)

    return dict(wiregauges = gauges, ods = ods, springprecision = springprecision, odprecision = odprecision, cycles = cycles)

# Create your views here.
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
    if request.method == 'POST':
        form = dict(request.POST)
        if form.get("orderid"):
            obj = models.Order.objects.get(pk = form.get("orderid")[0])
            if not obj: return  render(request,"doors/order.html",data)
            data = {key:obj.attr(key) for key in JOBVALIDKEYS}
        else:
            data = {key:"" for key in JOBVALIDKEYS}
        for key in JOBVALIDKEYS:
            if form.get(key): data[key] = form[key]
        data = cleanjobdata(data)
    else:
        error = False
        form = dict()
    data['form'] = form
    data['error'] = error
    return render(request,"doors/order.html",data)

@login_required
@decorators.require_GET
def orderinfo(request):
    """ Shows all components of a given order """
    if request.method == 'GET':
        orderid = request.GET['orderid']
        if not orderid:
            return order(request)
        doors = []
        for door in models.Door.objects.filter(order_id = orderid):
            components = []
            for obj in [models.BottomBar,models.CustomAccessory,models.Door,
                        models.Facia,models.FeederSlat,models.GearCover,models.Hood,
                        models.MotorCover,models.Pipe,models.Slats,models.Tracks]:
                components.extend(serializers.serialize("json",obj.objects.filter(order_id = orderid)))
            door.components = components
            doors.append(serializers.serialize("json",door))
        data = {"orderid":orderid,"doors":doors}
        return render(request,"doors/new_order.html",data)

@login_required
@decorators.require_GET
def orderpart(request):
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
        out = cleanoutput(obj,door)
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
        output,failures = validateorder(post)
        if nestedempty(failures):
            try:
                ## Use atomic transaction to automatically rollback if a discrepency arises
                with transaction.atomic():
                    customer = output['customer']

                    ## Create and Save Items in Order
                    customer,was_created = coremodels.Company.objects.get_or_create(name = customer)
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
                            raise ValidationException()
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
                  "width":measurement.minimizemeasurement(door.open_width),
                  "height":measurement.minimizemeasurement(door.open_height),
                  "hand":door.hand,"components":{"slats":[],"hood":[],"bottombar":[],"tracks":[],"pipe":[],"accessories":[]}}
        components = output['components']
        for pipe in models.Pipe.objects.filter(door = door):
            out = cleanoutput(pipe,door)
            comp = {"id": pipe.pk, "pipediameter":out['pipediameter'],"shaftdiameter":out['shaftdiameter'],"springs":out['springs']}
            components['pipe'].append(comp)
        for hood in models.Hood.objects.filter(door = door):
            out = cleanoutput(hood,door)            
            comp = {"id": out['pk'], "custom": out['custom'],"baffle":out['baffle']}
            components['hood'].append(comp)
        for tracks in models.Tracks.objects.filter(door = door):
            out = cleanoutput(tracks,door)
            comp = {"id": out['pk'], "brackets":{"hand":out['hand']}, "standard":out['standard'], "weatherstripping":out['weatherstripping']}
            components['tracks'].append(comp)
        for slats in models.Slats.objects.filter(door = door):
            out = cleanoutput(slats,door)
            comp = {"id": out['pk'], "slat_type":out['slat_type'], "quantity":out['quantity']}
            components['slats'].append(comp)
        for bottombar in models.BottomBar.objects.filter(door = door):
            out = cleanoutput(bottombar,door)
            comp = {"id": out['pk'], "slat_type":out['slat_type'],"angle":out['angle'],"bottom_rubber":out['bottom_rubber'],"slope":out['slope']}
            components['bottombar'].append(comp)
        for accessorytype in models.ACCESSORYLIST:
            names = []
            for accessory in accessorytype.objects.filter(door = door):
                out = cleanoutput(accessory,door)
                if out.get("kind") is not None:
                    names.append({"id":out['pk'], "name":out['kind']})
                else:
                    names.append({"id":out['pk'], "name":accessory.__class__.__name__})
        if names:
            components['accessories'].extend(names)                
        data['doors'].append(output)
    data = {"order":data}
    return render(request,template,data)

@login_required
@decorators.require_POST
def updatedoor(request):
    if request.method == "POST":
        doorid = request.POST.get("doorid")
        door = models.Door.objects.filter(pk = doorid).first()
        if not door:
            return dhttp.HttpResponseBadRequest("Invalid DoorID")
        return dhttp.HttpResponseBadRequest("Nope")
    else:
        return dhttp.HttpResponseBadRequest("Invalid Request")

def cleanoutput(obj, door):
    """ Returns a dict of values that are formatted for display """
    output = to_dict(obj)
    output['doorid'] = door.pk
    doorinstance = to_doorinstance(door)
    checkdefaults(doorinstance)
    
    if isinstance(obj,models.Pipe):
        pipeinstance = doorinstance.pipe
        sockets = pipeinstance.assembly.sockets
        springs = list(itertools.chain.from_iterable(sockets))
        output['springs'] = len(springs)
        ## Blank keys are converted to "Auto" for readability
        for autokey in ['pipelength','pipediameter','shaftlength','shaftdiameter','springs']:
            if not output[autokey]:
                if not springs:
                    output[autokey] = "Auto"
        ## If any of the following outputs are None, springs exist 
        ## and therefore the doorinstance has a value for them
        if not output['pipelength']:
            if pipeinstance.pipewidth:
                width = pipeinstance.pipewidth
            else:
                width = doorinstance.maxpipewidth()
            output['pipelength'] = f"{measurement.tomeasurement(roundtofraction(width,1/16))}"
        if not output['pipediameter']:
            output['pipediameter'] = f'{pipeinstance.shell["size"]}"'
        if not output['shaftlength']:
            output['shaftlength'] = f"{math.ceil(pipeinstance.required_shaftlength(doorinstance.totalturns))} inches"
        if not output['shaftdiameter']:
            output['shaftdiameter'] = f'{pipeinstance.shaft}"'

        output['assembly'] = list()
        for socket in sockets:
            for stype,spring in zip(["Outer","Inner"],socket.springs):
                out = dict(springtype = stype, wirediameter = spring.wirediameter, outerdiameter = spring.od, stretch = f"{roundtofraction(spring.stretch(doorinstance.totalturns),1/16)} inches")
                output['assembly'].append(out)

    elif isinstance(obj,models.Hood):
        if output['custom'] is True: output['custom'] = "Standard"
        else: output['custom'] = "Custom"
        width = obj.width
        if not width:
            width = doorinstance.hood.width
        output['width'] = width
    elif isinstance(obj,models.Tracks):
        bracket = obj.brackets

        output['standard'] = True
        if any([obj.wall_angle_height, obj.inner_angle_height, obj.outer_angle_height, obj.hole_pattern]):
            output['standard'] = False

        inner_angle_height = obj.inner_angle_height
        outer_angle_height = obj.outer_angle_height
        if not inner_angle_height and not outer_angle_height:
            inner_angle_height = doorinstance.stopheight
            outer_angle_height = inner_angle_height
        elif not outer_angle_height:
            outer_angle_height = inner_angle_height
        elif not inner_angle_height:
            inner_angle_height = outer_angle_height
        wall_angle_height = obj.wall_angle_height
        if not wall_angle_height:
            wall_angle_height = doorinstance.wall_length
        output['inner_angle_height'] = f"{inner_angle_height} ({measurement.minimizemeasurement(inner_angle_height)})"
        output['outer_angle_height'] = f"{outer_angle_height} ({measurement.minimizemeasurement(outer_angle_height)})"
        output['wall_angle_height'] = f"{wall_angle_height} ({measurement.minimizemeasurement(wall_angle_height)})"
        output['hole_pattern'] = obj.hole_pattern
            
        output['hand'] = bracket.hand
        if not output['hand']:
            output['hand'] = door.hand
        bracketsize = bracket.bracket_size
        if not bracketsize:
            bracketsize = doorinstance.bracketplate.size
        output['bracketsize'] = bracketsize
    elif isinstance(obj,models.Slats):
        slats = doorinstance.curtain[0]
        endlocks = obj.endlocks

        output['slat_type_name'] = obj.get_slat_type_display()
        output['quantity'] = obj.quantity
        output['facing'] = obj.get_face_display()
        if not output['quantity']:
            output['quantity'] = "Auto"
            output['slatquantity'] = slats.getnumberslats()
        if not output['width']:
            output['width'] = measurement.tomeasurement(doorinstance.curtain.slatlength(slats))
        output['width'] = f"{measurement.minimizemeasurement(output['width'])} ({measurement.convertmeasurement(output['width'])})"
        if endlocks:
            output['endlocktype'] = endlocks.get_endlock_type_display()
            output['endlockcontinuous'] = endlocks.continuous
            elocks,windlocks = slats.endlockpattern.getendlocks(output['slatquantity'])
            output['endlockquantity'] = elocks
            output['windlockquantity'] = windlocks

    elif isinstance(obj,models.BottomBar):
        bbar = doorinstance.curtain[-1]

        output['face_name'] = obj.get_face_display()
        output['slat_type_name'] = obj.get_slat_type_display()
        if not output['width']:
            output['width'] = measurement.tomeasurement(bbar.slatlength)
        output['width'] = f"{measurement.minimizemeasurement(output['width'])} ({measurement.convertmeasurement(output['width'])})"
        if output['angle'] == "D": output['angle'] = "Double"
        else: output['angle'] = "Single"
        if not output['slope_height']: output['slope'] = False
        else:
            output['slope'] = True
            output['slope_height'] = f"{measurement.minimizemeasurement(output['slope_height'])} ({measurement.convertmeasurement(output['slope_height'])})"
            output['slope_side_name'] = obj.get_slope_side_display()
    elif isinstance(obj,models.ACCESSORYLIST):
        if obj.get("kind") is not None:
            output["name"]=out['kind']
        else:
            output["name"]=obj.__class__.__name__

    return output

def _set_slats(doorinstance):
    """ Helper function for automatically populating slats (when slats are not explicitly set) """
    slatsection = doorinstance.curtain.slatsections()[0]
    slatsection.slats = slatsection.getnumberslats(doorinstance.curtain.curtainshort())

@login_required
@decorators.require_GET
def springsetter(request,doorid = None):
    """ Displays various spring options for a given door """
    template = "doors/springsetter.html"
    if not request.method == "GET":
        return dhttp.HttpResponseNotAllowed(["GET",])
    if not doorid:
        data = dict()
        return render(request,template,data)
    
    door = models.Door.objects.filter(doorid=doorid).first()
    if not door:
        return dhttp.HttpResponseBadRequest("Invalid Door ID")

    doorinstance = to_doorinstance(door)
    checkdefaults(doorinstance)

    data = getspringoptions()
    data.update(dict(doorid = None, name = None, cyclerating = None, pipesizes = None, weightopen = None, weightclosed = None))
    data['doorid'] = doorid
    data['name'] = door.name
    data['cyclerating'] = doorinstance.pipe.cycles
    data['pipesizes'] = [(pipe,stats['radius']+stats['barrelringsize']) for pipe,stats in classes.PIPESIZES.items()]
    if doorinstance.curtain.slatsections():
        data['weightopen'],data['weightclosed'] = doorinstance.curtain.weight_open,doorinstance.curtain.weight_closed
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
    if doorid is None:
        return dhttp.HttpResponseServerError("Not Implemented")
    door = models.Door.objects.filter(doorid=doorid).first()
    if not door:
        return dhttp.HttpResponseBadRequest("Invalid Door ID")
    
    pipe = data.get("pipe")
    doorinstance = to_doorinstance(door)
    if pipe:
        doorinstance.pipe.shell =pipe
    if not doorinstance.pipe.shell:
        return dhttp.HttpResponseBadRequest("Invalid Pipe")

    _set_slats(doorinstance)

    assemblies = classes.generate_all_assemblies(doorinstance.torqueperturn, doorinstance.totalturns, pipe = doorinstance.pipe)
    output= []
    ## index is used for generically naming Assemblies:
    ## i.e.- "1-Spring Assembly", "1-Spring Assembly - 2", "2-Spring Assembly", etc
    index = collections.defaultdict(int)

    def outputSpring(spring):
        return {"gauge":spring.wirediameter, "od":spring.od, "coils": spring.coils}

    for assembly in assemblies:
        i = 0
        out = {'castings' : []}
        output.append(out)
        for socket in assembly.sockets: ## Sockets are Castings
            o = []
            out['castings'].append(o)
            for spring in socket.springs:
                if not isinstance(spring,classes.Spring):
                    raise ValueError("Unknown Socket Element")
                o.append(outputSpring(spring))
                i+=1
        if index[i] == 1: count = ""
        else: count = f" - {index[i]}"
        index[i] += 1
        out['name'] = f"{i}-Spring Assembly{count}"
    return dhttp.JsonResponse({"success":True,"results":{'assemblies':output} })

@login_required
@decorators.require_GET
def API_turns(request):
    data = request.GET
    doorid = data.get("doorid")
    if doorid is None:
        return dhttp.HttpResponseServerError("Not Implemented")
    door = models.Door.objects.filter(doorid=doorid).first()
    if not door:
        return dhttp.HttpResponseBadRequest("Invalid Door ID")
    
    doorinstance = to_doorinstance(door)
    pipe = data.get("pipe")
    if not pipe:
        if not doorinstance.pipe.shell:
            return dhttp.HttpResponseBadRequest("Door requires Pipe Size")
    else:
        doorinstance.pipe.shell = pipe

    _set_slats(doorinstance)
    return dhttp.JsonResponse({"success":True,"results":{"turns":doorinstance.totalturns,"turnstoraise":doorinstance.turnstoraise,"preturns":doorinstance.preturns}})

@login_required
@decorators.require_GET
def API_torque(request):
    data = request.GET
    doorid = data.get("doorid")
    if doorid is None:
        return dhttp.HttpResponseServerError("Not Implemented")
    door = models.Door.objects.filter(doorid=doorid).first()
    if not door:
        return dhttp.HttpResponseBadRequest("Invalid Door ID")
    
    doorinstance = to_doorinstance(door)
    pipe = data.get("pipe")
    if not pipe:
        if not doorinstance.pipe.shell:
            return dhttp.HttpResponseBadRequest("Door requires Pipe Size")
    else:
        doorinstance.pipe.shell = pipe

    _set_slats(doorinstance)
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
        castings = assembly.get("castings")
    if not assembly or not castings:
        return dhttp.JsonResponse({"success":False,"reason":"nocastings"})
    
    doorinstance = to_doorinstance(door)
    doorinstance.pipe.shell = pipesize

    _set_slats(doorinstance)
    
    assemblyinstance = doorinstance.pipe.assembly
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
                          casting = c).save()

    orderid = door.order.pk
    return dhttp.JsonResponse({"success":True,"target": reverse("orderoverview",args = (orderid,))})

@login_required
def searchorder(request):
    pass