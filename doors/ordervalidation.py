""" BRDWebApp/doors/ordervalidation.py

    Contains methods for validating the order and 
"""

## Backend
import django.utils.html as dhtml
## This package
from core import models as coremodels
from . import models
## Sister Module
from NewDadsDoor import classes, methods

## Builtin
import datetime
## Custom Module
from alcustoms.methods import nestedempty
from alcustoms import measurement

JOBVALIDKEYS = ['customer','customer_po','work_order','origin_date','due_date',"description"]

def validateorder(post):
    """ Validatesd data posted to ordervalidation method """
    output = {"customer":None, "job":None,"doors":list()}
    failures = {'job':None,'doors':list()}
    jobdata = cleanjobdata(post)
    output['customer'] = jobdata['customer']
    obj,fail = jobvalid(jobdata)
    output['job'] = obj
    failures['job'] = fail
    for i,door in enumerate(post['doors']):
        objs,fails = validatedoor(door)
        if not nestedempty(fails):
            fails['index'] = i
            failures['doors'].append(fails)
        else:
            output['doors'].append(objs)
    return output,failures

def cleanjobdata(data):
    """ Cleans the job data """
    data = {key:dhtml.escape(data.get(key,"")) for key in JOBVALIDKEYS}
    try: data['origin_date'] = datetime.datetime.strptime(data['origin_date'],DATEINPUTFORMAT)
    except:
        try: data['origin_date'] = datetime.datetime.strptime(data['origin_date'],DATEFORMAT)
        except: data['origin_date'] = datetime.datetime.today()
    try: data['due_date'] = datetime.datetime.strptime(data['due_date'],DATEINPUTFORMAT)
    except:
        try: data['due_date'] = datetime.datetime.strptime(data['due_date'],DATEFORMAT)
        except: data['due_date'] = datetime.datetime.today()
    return data

def jobvalid(data):
    """ Validates the form data received from the New Job Form.
    
        If the data is valid, returns an Order Model instance and an empty list of Failures.
        Otherwise, returns None and a list of Failures.
    """
    output = None
    failures = list()
    for (test,response) in [
        ## Customer should be a string
        (lambda: isinstance(data['customer'],str),"Invalid Customer"),
        ## Customer PO should be a string or None
        (lambda: isinstance(data['customer_po'],str) or data['customer_po'] is None,"Invalid Customer PO"),
        ## Work Order should be a string or None
        (lambda: isinstance(data['work_order'],str) or data['work_order'] is None, "Bad Work Order"),
        ## Origin Date should be a datetime.datetime
        (lambda: isinstance(data['origin_date'],datetime.datetime), "Bad Origin Date"),
        ## Due Date should be a datetime.datetime
        (lambda: isinstance(data['due_date'],datetime.datetime), "Bad Due Date"),
        ## Origin Date should be before or the same as Due Date
        (lambda: data['origin_date'] <= data['due_date'], "Bad Origin or Due Date"),
        ]:
        try:
            if not test(): failures.append(response)
        except: failures.append(response)            

    if nestedempty(failures):
        output = models.Order(origin_date = data['origin_date'], due_date = data['due_date'], customer = None, customer_po = data['customer_po'], work_order = data['work_order'], description = data['description'])
    return output, failures


def validatedoor(_door):
    """ Validates the given door

    Outputs two values: a dict of objects, and a dict which contains any errors for those objects.
    The objects dict is formatted {"door":Door Object, "components":[ *Component Objects]}.
    The error dict is formatted {"door":[*door errors], "components":[ [ *component errors] for each component]}.
    It is recommended to use nestedempty() (imported into this module from alcustoms.methods) to quickly check
    if the error dict contains errors.
    """
    output = {"door":None,"components":[]}
    failures = {"door":[],"components":[]}

    ## Build and validate door
    name,width,height,hand = _door['name'],_door['clearwidth'],_door['clearheight'],_door['hand']
    door = models.Door(name = name, open_width = width, open_height = height, hand = hand)
    output['door'] = door
    if not models.run_validations(door):
        failures['door'].append("Invalid Door")
    ## TODO: Figure out how we're going to update specific errors
    #if not door.validate_height(): failures['door'].append("Invalid Clear Height")
    #if not door.validate_width(): failures['door'].append("Invalid Clear Width")
    
    ## Validate Each component
    for component in _door['components']:
        comptype = component['type']
        if comptype == "slats": method,kw = validateslats, {"openwidth":door.open_width}
        elif comptype == "hood": method,kw = validatehood, {"openwidth":door.open_width}
        elif comptype == "bottombar": method,kw = validatebottombar, {"openwidth":door.open_width}
        elif comptype == "tracks": method,kw = validatetracks, {"openheight":door.open_height, "hand":hand}
        elif comptype == "pipe":
            ## component['cycles'] = _door['cycles'] ## This is probably safe to delete
            method,kw = validatepipe, {"openwidth":door.open_width, "hand":hand}
        elif comptype == "accessories": method,kw = validateaccessories, {}
        else:
            failures['components'].append([f"Unknown Component: {comptype}"])
            continue
        ## Run validation method
        try:
            obj,fail = method(door,component,**kw)
        except Exception as e:
            obj = None
            import traceback
            traceback.print_exc()
            fail = [f"{comptype} Failure: {e}",]
        ## update both return values
        ## obj may be a list of related objects
        if isinstance(obj,list): output['components'].extend(obj)
        else: output['components'].append(obj)
        if not nestedempty(fail):
            failures['components'].extend(fail)
    
    ## Since adding the name will make the failures non-empty, 
    ## we want to wait until the very end to do so
    if not nestedempty(failures):
        failures['name'] = name

    ## return values
    return output,failures

def validateslats(door,_slats,openwidth = None):
    """ Validates a set of slats.

    Accepts a width to compare the width of the slats to.
    Returns a list with a Slats Model and a Endlocks Model instance and a list containing any errors that may have arisen.
    """
    failures = []
    slat_type = _slats['slattype']
    width = _slats['slatlength']
    quantity = _slats['slatquantity']
    assemble = _slats['assembled']
    face = _slats['facing']
    endlock_type = _slats['endlocks']
    if isinstance(width,str): width = measurement.convertmeasurement(width)
    continuous = _slats['continuousendlocks']
    if continuous == "on": continuous = True
    else: continuous = False
    if _slats['autolength'] == "Auto": width = None
    if _slats['autoquantity'] == "Auto": quantity = None
    if face == "Interior": face = "I"
    elif face == "Exterior": face = "E"
    else: failures.append("Invalid Facing")
    if assemble == "Assembled": assemble = "A"
    elif assemble == "Loose": assemble = "U"
    else: failures.append("Invalid Assembly")

    endlocks = models.Endlocks(endlock_type = endlock_type, continuous = continuous)
    try: endlocks.clean_fields()
    except Exception as e: failures.append(f"Endlock Error:{e}")
    slats = models.Slats(slat_type = slat_type, width = width, quantity = quantity, assemble = assemble, face = face, endlocks = endlocks)
    if not models.run_validations(slats): failures.append("Invalid Slat Width")
    try: slats.clean_fields()
    except Exception as e: failures.append(f"Slat Failures: {e}")
    return {"object":slats,"endlocks":endlocks},failures

def validatehood(door,_hood,openwidth = None):
    """ Validates a hood.

    Accepts a width to compare the width of the hood to.
    Returns a Hood Model instance and a list containing any errors that may have arisen.
    """
    failures = []
    if _hood['standardhood'] == "Standard":
        custom = False
        width = None
        description = None
    elif _hood['standardhood'] == "Custom":
        custom = True
        if _hood['autolength'] == "Auto":
            width = None
        elif _hood['autolength'] == "Manual":
            width = _hood['hoodlength']
        else:
            failures.append("Invalid AutoLength")
        description = _hood['hooddescription']
    else: failures.append("Invalid Hood Customization")
    if _hood['baffle'] == "None": baffle = False
    elif _hood['baffle'] == "Include": baffle = True
    else: failures.append("Invalid Hood Baffle")
    hood = models.Hood(custom = custom, width = width, baffle=baffle, description = description)
    try: hood.clean_fields()
    except Exception as e: failures.append(f"Hood Failures: {e}")

    return hood,failures

def validatebottombar(door,bbar, openwidth = None):
    """ Validates a bottombar.

    Accepts a width to compare the width of the bottombar to.
    Returns a Bottombar Model instance and a list containing any errors that may have arisen.
    """
    failures = []
    slat_type = bbar['slattype']
    face = bbar['facing']
    width = bbar['slatlength']
    angle = bbar['angle']
    bottom_rubber = bbar['bottomrubber']
    slope_height = bbar['slopeheight']
    slope_side = bbar['slopelongside']

    autolength = bbar['autolength']
    slope = bbar['slope']
    if autolength == "Auto":
        width = None
    elif autolength != "Manual":
        failures.append("Invalid Autolength")
    if slope == "Standard":
        slope_height = None
    if face == "Interior": face = "I"
    elif face == "Exterior": face = "E"
    else: failures.append("Invalid Facing")
    if angle == "double": angle = "D"
    elif angle == "single": angle = "S"
    else: failures.append("Invalid Angle")
    if slope_side == "Right": slope_side = "R"
    elif slope_side == "Left": slope_side = "L"
    else: failures.append("Invalid Slope Side")
    
    bottombar = models.BottomBar(slat_type = slat_type, face = face, width = width, angle = angle,
                                 bottom_rubber = bottom_rubber, slope_height = slope_height, slope_side = slope_side)
    try: bottombar.clean_fields()
    except Exception as e: failures.append(f"BottomBar Failures: {e}")

    return bottombar,failures

def validatetracks(door,track, openheight = None, hand = None):
    """ Validates a bottombar.

    Accepts a height to compare the track height to and hand to compare the Bracket Plates to.
    Returns a Bottombar Model instance and a list containing any errors that may have arisen.
    """
    failures = []
    bracket_size = track['bracketsize']
    hand = track['hand']
    wall_angle_height = track['wallangleheight']
    inner_angle_height = track['guideheight']
    outer_angle_height = track['guideheight']
    hole_pattern = track['Guide Holes']
    weatherstripping = track['weatherstripping']

    autobrackets = track['autobrackets']
    autowall = track['autowallangleheight']
    autoguide = track['autoguideheight']
    if autobrackets == "Auto":
        bracket_size = None
        hand = None
    elif autobrackets != "Manual":
        failures.append("Invalid Autobrackets")
    else:
        if hand == "Right": hand = "R"
        elif hand == "Left": hand = "L"
        else:
            failures.append("Invalid Bracket Hand")
    if autowall == "Auto":
        wall_angle_height = None
    elif autowall != "Manual":
        failures.append("Invalid Autowallangleheight")
    if autoguide == "Auto":
        inner_angle_height, outer_angle_height = None, None
    elif autoguide != "Manual":
        failures.append("Invalid Autoguideheight")
    if weatherstripping == "None":
        weatherstripping = False
    elif weatherstripping == "Include":
        weatherstripping = True
    else:
        failures.append("Invalid Weatherstripping")

    brackets = models.Brackets(bracket_size = bracket_size, hand = hand)
    tracks = models.Tracks(brackets = brackets, wall_angle_height = wall_angle_height,
                           inner_angle_height = inner_angle_height, outer_angle_height = outer_angle_height,
                           hole_pattern = hole_pattern, weatherstripping = weatherstripping)

    try: brackets.clean_fields()
    except Exception as e: failures.append(f"Bracket Failures: {e}")
    if hand and brackets.hand and (brackets.hand != hand):
        failures.append("Invalid Bracket Hand")

    try: tracks.clean_fields()
    except Exception as e: failures.append(f"Track Failures: {e}")

    return {"object":tracks,"brackets":brackets}, failures

def validatepipe(door,_pipe, openwidth=None, hand=None):
    """ Validates a pipe.

    Accepts a width to compare the pipe width to and hand to compare the Drive Side to.
    Returns a Pipe Model instance and a list containing any errors that may have arisen.
    """
    objects = {"object":None, "springs": []}
    failures = []

    pipelength = _pipe['pipelength']
    pipediameter = _pipe['pipediameter']
    shaftlength = _pipe['shaftlength']
    shaftdiameter = _pipe['shaftdiameter']
    autopipe = _pipe['autocalculation']
    cycles = _pipe['cycles']
    if autopipe == "Auto":
        pipelength,pipediameter = None,None
        shaftlength, shaftdiameter = None,None
        cycles = 12500
    elif _pipe['autocalculation'] != "Manual":
        failures.append("Invalid Pipe autocalculation")

    pipe = models.Pipe(door = door,
                       pipelength = pipelength, pipediameter = pipediameter,
                       shaftlength = shaftlength, shaftdiameter = shaftdiameter,
                       cycles = cycles)

    try: pipe.clean_fields()
    except:
        import traceback
        traceback.print_exc()
        failures.append("Pipe Failure")
    else:
        objects['object'] = pipe

    for spring in _pipe['springs']:
        obj,fails = validatespring(spring,pipe)
        objects['springs'].append(obj)
        failures.append(fails)

    return objects,failures

def validatespring(_spring,pipe):
    """ Validates a Spring.

    Returns a Spring Model Instance and a list containing any errors that may have arisen.
    """
    failures = []

    spring_type = _spring['springtype']
    if spring_type == "outer": spring_type = "O"
    elif spring_type == "inner": spring_type = "I"
    else: failures.append("Invalid Spring Type")
    outer_diameter = _spring['springod']
    wire_diameter = _spring['springdiameter']
    stretch = _spring['springstretch']
    
    spring = models.Spring(pipe = pipe, spring_type = spring_type, outer_diameter = outer_diameter, wire_diameter = wire_diameter, stretch = stretch)
    try: spring.clean_fields()
    except Exception as e: failures.append(f"Invalid Spring: {e}")

    return spring, failures

def validateaccessories(door,_accessory):
    """ Validates an Accessory.

    Returns an Accessory Model instance and a list containing any errors that may have arisen.
    """
    failures = []
    accessory = None
    kind = _accessory['accessorytype']
    description = _accessory.get("description")
    if kind in ["foc","chainplate","slidelocks","pinlocks"]:
        accessory = models.Accessory(kind = kind, door = door, description = description)
    elif kind == "":
        name = _accessory['name']
        accessory = models.CustomAccessory(kind = kind, door = door, description = description,name = name)
    elif kind in ["brackets","motorcover","gearcover"]:
        hand = _accessory['hand']
        if hand == "Right": hand = "R"
        elif hand == "LEFT": hand = "L"
        else:
            failures.append("Invalid hand")
        if kind == "motorcover":
            accessory = models.MotorCover(kind = kind, door = door, description = description, hand = hand)
        elif kind == "gearcover":
            accessory = models.GearCover(kind = kind, door = door, description = description, hand = hand)
        elif kind == "brackets":
            _type = _accessory['brackettype']
            if _type == "Drive": _type = "D"
            elif _type == "Charge": _type = "C"
            else: failures.append("Invalid Bracket Type")
            accessory = models.AccessoryBrackets(door = door, hand = hand, type = _type)
    elif kind == "facia":
        width = _accessory['width']
        height = _accessory['height']
        autowidth = _accessory['autowidth']
        autoheight = _accessory['autoheight']
        if autowidth == "Auto":
            width = None
        elif autowidth != "Manual":
            failures.append("Invalid Facia")
        if autoheight == "Auto":
            height = None
        elif autoheight != "Manual":
            failures.append("Invalid Facia")
        accessory = models.Facia(kind = kind, door = door, description = description,length = width, height = height)
    elif kind == "feederslat":
        length = _accessory['slatlength']
        autolength = _accessory['autolength']
        if autolength == "Auto":
            length = None
        elif autolength != "Manual":
            failures.append("Invalid Feederslat")
        face = _accessory['facing']
        if face == "Exterior": face = "E"
        elif face == "Interior": face = "I"
        else: failures.append("Invalid Feederslat Facing")
        slattype = _accessory['slattype']
        accessory = models.FeederSlat(kind = kind, door = door, description = description,length = length, face = face, slattype = slattype)
    elif kind == "hardware":
        name = _accessory['hardware']
        quantity = _accessory['quantity']
        if name == "endlocks":
            _type = _accessory['endlocks']
            accessory = models.HardwareEndlocks(kind = kind, door = door, description = description, name = name, quantity = quantity, type = _type)
        elif name in ['rivets','washers']:
            accessory = models.Hardware(kind = kind, door = door, description = description, name = name, quantity = quantity)
        else:
            failures.append("Invalid Hardware Type")
    else:
        failures.append("Unknown Accessory Type")

    try:
        accessory.clean_fields()
    except Exception as e:
        failures.append(f"Invalid {accessory}: {e}")
    return accessory, failures

def checkdefaults(doorinstance):
    """ Checks for any vital missing values (due to Auto-calculate) and fills them in with default values """
    if not doorinstance.tracks:
        methods.create_tracks(doorinstance)
    if not doorinstance.tracks.outer:
        doorinstance.tracks.outer = doorinstance.clearopening_height + doorinstance.tracks.stopsize
    if not doorinstance.tracks.inner:
        doorinstance.tracks.inner = doorinstance.clearopening_height + doorinstance.tracks.stopsize
    if not doorinstance.tracks.wall:
        doorinstance.tracks.wall = doorinstance.wall_length()
    if not doorinstance.pipe.shell:
        doorinstance.pipe.shell = 4
    if doorinstance.curtain.slatsections():
        slatsection = doorinstance.curtain.slatsections()[0]
        ## Our online App does not do custom slat counts currently, so it has to be filled in
        slatsection.slats = slatsection.getnumberslats(doorinstance.curtain.curtainshort())

def _set_slats(doorinstance):
    """ Helper function for automatically populating slats (when slats are not explicitly set) """
    slatsection = doorinstance.curtain.slatsections()[0]
    if not slatsection.slats:
        slatsection.slats = slatsection.getnumberslats(doorinstance.curtain.curtainshort())