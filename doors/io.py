""" BRDWebApp/doors/io.py

    A Collection of methods for interpolation between different modules
    and outputs.
"""
## Backend
from django.db.models.fields.related import ManyToManyField,ForeignKey
## This Package
from . import models
from . import ordervalidation as oval
## Sister Module
from NewDadsDoor import classes

## Builtin
import datetime
import itertools
import math
## Custom Module
from alcustoms.methods import roundtofraction
from alcustoms import measurement

def to_dict(instance):
    """ Converts an object instance to a dictionary, preserving as many fields as possible
    
        Stolen (and modified) from: https://stackoverflow.com/a/29088221/3225832
    """
    opts = instance._meta
    data = {}
    for f in opts.concrete_fields + opts.many_to_many:
        if isinstance(f, ManyToManyField):
            if instance.pk is None:
                data[f.name] = []
            else:
                data[f.name] = list(f.value_from_object(instance).values_list('pk', flat=True))
        elif isinstance(f,ForeignKey):
            data[f.name] = to_dict(getattr(instance,f.name))
        else:
            data[f.name] = f.value_from_object(instance)
    data['pk'] = instance.pk
    return data

def to_doorinstance(doorobj):
    """ Converts a Django Door Model to a NewDadsDoor Door Instance (as well as all components) """

    if not isinstance(doorobj,models.Door):
        raise ValueError("to_doorinstance only accepts a Door Model instance")

    doorinstance = classes.Door(**doorobj.to_kwargs())

    hood = doorinstance.sethood()

    tracksobj = models.Tracks.objects.filter(door = doorobj.pk).first()

    tracks = doorinstance.settracks()
    if tracksobj:
        doorinstance.bracketplatesize = tracksobj.brackets.bracket_size
        if tracksobj.outer_angle_height:
            tracks.outer = tracksobj.outer_angle_height
        if tracksobj.inner_angle_height:
            tracks.inner = tracksobj.inner_angle_height
        if tracksobj.wall_angle_height:
            tracks.wall = tracksobj.wall_angle_height

    pipeobj = models.Pipe.objects.filter(door = doorobj.pk).first()
    if pipeobj:
        pipe = doorinstance.setpipe(**pipeobj.to_kwargs())
        assembly = pipe.setassembly()

        springs = models.Spring.objects.filter(pipe = pipeobj.pk)
        castings = sorted(list(set(spring.casting for spring in springs if spring is not None)))
        for casting in castings:
            ## Instead of referencing spring_type to determine order, we're just going to sort the od
            spngs = sorted(springs.filter(casting = casting), key = lambda spring: spring.outer_diameter, reverse = True)
            spngs = [classes.Spring(**spring.to_kwargs()) for spring in spngs]
            socket = classes.Socket(*spngs)
            assembly.addsocket(socket)

    else:
        pipe = doorinstance.setpipe()
        assembly = pipe.setassembly()

    curtain = doorinstance.setcurtain()
    for slatobj in models.Slats.objects.filter(door = doorobj.pk):
        slats = classes.SlatSection(curtain = curtain, **slatobj.to_kwargs())
        curtain.append(slats)

    bbarobj = models.BottomBar.objects.filter(door = doorobj.pk).first()
    if bbarobj:
        bbar = classes.BottomBar(**bbarobj.to_kwargs())
        curtain.append(bbar)

    accessories = []
    for accessorytype in models.ACCESSORYLIST:
        for accessory in accessorytype.objects.filter(door = doorobj.pk):
            o = {"kind":accessory.kind, "description":accessory.description}
            ## TODO: expand this
            accessories.append(o)

    doorinstance.accessories = accessories
    return doorinstance

def cleanoutput(obj, door):
    """ Returns a dict of values that are formatted for display """
    output = to_dict(obj)
    output['doorid'] = door.pk
    doorinstance = to_doorinstance(door)
    oval.checkdefaults(doorinstance)
    
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
                out = dict(springtype = stype, wirediameter = spring.wirediameter, outerdiameter = spring.od, coiledlength = spring.coiledlength, stretch = f"{roundtofraction(spring.stretch(doorinstance.totalturns),1/16)} inches")
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
            wall_angle_height = doorinstance.wall_length()
        print(wall_angle_height)
        output['inner_angle_height'] = f"{inner_angle_height} ({measurement.minimizemeasurement(measurement.tomeasurement(inner_angle_height))})"
        output['outer_angle_height'] = f"{outer_angle_height} ({measurement.minimizemeasurement(measurement.tomeasurement(outer_angle_height))})"
        output['wall_angle_height'] = f"{wall_angle_height} ({measurement.minimizemeasurement(measurement.tomeasurement(wall_angle_height))})"
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
        output['slatquantity'] = obj.quantity
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
            output['width'] =bbar.slatlength
        output['width'] = f"{measurement.minimizemeasurement(measurement.tomeasurement(output['width']))} ({output['width']})"
        if output['angle'] == "D": output['angle'] = "Double"
        else: output['angle'] = "Single"
        if not output['slope_height']: output['slope'] = False
        else:
            output['slope'] = True
            output['slope_height'] = f"{measurement.minimizemeasurement(measurement.tomeasurement(output['slope_height']))} ({output['slope_height']})"
            output['slope_side_name'] = obj.get_slope_side_display()
    elif isinstance(obj,models.ACCESSORYLIST):
        if obj.get("kind") is not None:
            output["name"]=out['kind']
        else:
            output["name"]=obj.__class__.__name__

    def serialize_dates(_indict):
        for k,v in list(_indict.items()):
            if isinstance(v,(datetime.date,datetime.datetime)):
                _indict[k] = str(v)
            elif isinstance(v,dict):
                serialize_dates(v)

    serialize_dates(output)

    return output

def serialize_assembly(assembly):
    """ Serializes an assembly """
    def outputSpring(spring):
        return {"gauge":spring.wirediameter, "od":spring.od, "coils": spring.coils}
    out = {'castings' : []}
    for socket in assembly.sockets: ## Sockets are Castings
        o = []
        out['castings'].append(o)
        for spring in socket.springs:
            if not isinstance(spring,classes.Spring):
                raise ValueError("Unknown Socket Element")
            o.append(outputSpring(spring))
    return out