## Backend
from django.db import models
from django.core import exceptions

## This Module
from core import models as coremodels

## Sister Module
from NewDadsDoor import classes

## Custom Module
from alcustoms import measurement

SLATS = (
        ("BRD","BRD Slats"),
        ("NY", "New York Slats"),
        ("CRN", "Crown Slats"),
        ("MCR", "Mini Crown Slats")
        )

FACES = (
    ("I","Interior"),
    ("E","Exterior")
    )

HAND = (
    ("R","Right"),
    ("L","Left")
    )

ENDLOCKS = (
    ("FLSTP", "Flat Stamped"),
    ("FLCST", "Flat Cast"),
    ("FLCWD", "Flat Cast Windlock"),
    ("CRCST", "Curved Cast"),
    ("CRCWD", "Curved Cast Windlock"),
    ("MNCST", "Mini Cast")
    )

def validate_measurement(measure):
    """ Convenience function for making sure a measurement
        value conforms to the standard parsing requirements.
    """
    ## For auto-calculation, just succeed
    if not measure: return True
    inches = measurement.convertmeasurement(measure)
    return isinstance(inches,float) and inches > 0

def run_validations(model):
    for (name,method) in model.VALIDATIONS:
        if not method(model):
            raise exceptions.ValidationError(f"Invalid format for field {name}")

# Create your models here.
class Order(models.Model):
    """ Outlines hard information about an order """
    orderid = models.AutoField(primary_key = True)
    date = models.DateField(auto_now=True)
    origin_date = models.DateField()
    due_date = models.DateField()
    customer = models.ForeignKey(coremodels.Company, on_delete=models.DO_NOTHING, blank = True)
    customer_po = models.CharField(max_length = 50, blank = True, null = True)
    work_order = models.CharField(max_length = 50, blank = True, null = True)
    description = models.CharField(max_length = 100, blank = True, null = True)

class Door(models.Model):
    """ Gives general information about a specific Door """
    doorid = models.AutoField(primary_key = True)
    order = models.ForeignKey('Order',models.DO_NOTHING, blank = True)
    name = models.CharField(max_length = 50)
    open_width = models.CharField(max_length = 50)
    open_height = models.CharField(max_length = 50)
    hand = models.CharField(max_length = 40, choices = HAND)

    def clean_fields(self,exclude = None):
        run_validations(self)
        return super().clean_fields(self,exclude = exclude)
    def validate_height(self):
        return validate_measurement(self.open_height)
    def validate_width(self):
        return validate_measurement(self.open_width)
    VALIDATIONS = [("height",validate_height),
                   ("width",validate_width)]

    def to_kwargs(self):
        return dict(clearopening_height=self.open_height, clearopening_width= self.open_width)

class Hood(models.Model):
    hoodid = models.AutoField(primary_key = True)
    door = models.ForeignKey("Door", models.DO_NOTHING, blank = True)
    custom = models.BooleanField(null = False,blank = False)
    width = models.CharField(max_length = 50, null = True, blank = True)
    baffle = models.BooleanField(null = False, default = False)
    description = models.TextField(null = True, blank = True)

    def clean_fields(self, exclude = None):
        run_validations(self)
        return super().clean_fields(exclude)
    def validate_width(self):
        if self.width:
            return validate_measurement(self.width)
        return True
    VALIDATIONS = [("width",validate_width),
        ]

class Brackets(models.Model):
    bracketid = models.AutoField(primary_key = True)
    bracket_size = models.CharField(max_length = 50, blank = True, null = True)
    hand = models.CharField(max_length = 50, choices = HAND, blank = True, null = True)

class Pipe(models.Model):
    CYCLES = (
        ('12500','12500'),
        ('25000','25000'),
        ('50000','50000'),
        ('100000','100000'),
        ('16500','16500'),
        )

    pipeid = models.AutoField(primary_key = True)
    door = models.ForeignKey("Door", models.DO_NOTHING, blank = True, null = True)
    pipelength = models.CharField(max_length = 50, blank = True, null = True)
    pipediameter = models.CharField(max_length = 50, blank = True, null = True)
    shaftlength = models.CharField(max_length = 50, blank = True, null = True)
    shaftdiameter = models.CharField(max_length = 50, blank = True, null = True)
    cycles = models.CharField(choices = CYCLES, max_length = 50)

    def getclearopen(self):
        return self.pipelength

    def clean_fields(self, exclude = None):
        run_validations(self)
        return super().clean_fields(exclude)
    def validate_pipelength(self):
        if self.pipelength:
            return validate_measurement(self.pipelength)
        return True
    def validate_shaftlength(self):
        if self.shaftlength:
            return validate_measurement(self.shaftlength)
        return True
    VALIDATIONS = [("pipelength",validate_pipelength),
                   ("shaftlength",validate_shaftlength),
        ]

    def to_kwargs(self):
        kwargs = dict()
        if self.pipelength:
            kwargs['pipewidth'] = self.pipelength
        if self.pipediameter:
            kwargs['shell'] = self.pipediameter
        kwargs['cycles'] = self.cycles
        return kwargs

class Spring(models.Model):
    TYPE = ( ("I","Inner") , ("O","Outer") )
    springid = models.AutoField(primary_key = True)
    pipe = models.ForeignKey("Pipe", models.CASCADE, blank = True)
    spring_type = models.CharField(max_length = 50, choices = TYPE)
    outer_diameter = models.FloatField()
    wire_diameter = models.FloatField()
    uncoiledlength = models.FloatField()

    casting = models.IntegerField(blank = True, null = True)

    def to_kwargs(self):
        return dict(wire = self.wire_diameter, od = self.outer_diameter, uncoiledlength = self.uncoiledlength)

class Tracks(models.Model):
    trackid = models.AutoField(primary_key = True)
    door = models.ForeignKey("Door", models.DO_NOTHING, blank = True)
    brackets = models.ForeignKey("Brackets", models.DO_NOTHING, blank = True, null = True)
    wall_angle_height = models.CharField(max_length = 50, blank = True, null = True)
    inner_angle_height = models.CharField(max_length = 50, blank = True, null = True)
    outer_angle_height = models.CharField(max_length = 50, blank = True, null = True)
    hole_pattern = models.TextField(blank = True, null = True)
    weatherstripping = models.BooleanField(null = False, default = False)
    
    def clean_fields(self, exclude = None):
        run_validations(self)
        return super().clean_fields(exclude)
    def validate_height(self):
        if self.height:
            return validate_measurement(self.height)
        return True
    VALIDATIONS = [("height",validate_height),
        ]

class Slats(models.Model):
    ASSEMBLE = (
        ("A","Assembled"),
        ("U","Unassembled")
        )
    slatid = models.AutoField(primary_key = True)
    door = models.ForeignKey("Door", models.DO_NOTHING, blank = True)
    slat_type = models.CharField(choices = SLATS,max_length = 50)
    width = models.CharField(max_length = 50,null = True, blank = True)
    quantity = models.PositiveIntegerField(null = True, blank = True)
    assemble = models.CharField(max_length = 50, choices = ASSEMBLE)
    face = models.CharField(max_length = 50, choices = FACES)
    endlocks = models.ForeignKey("Endlocks", models.CASCADE, blank = True, null = True)
    

    def clean_fields(self, exclude = None):
        run_validations(self)
        return super().clean_fields(exclude)
    def validate_width(self):
        if self.width:
            return validate_measurement(self.width)
        return True
    VALIDATIONS = [("width",validate_width),
        ]

    def to_kwargs(self):
        endlockpattern = None
        if self.endlocks:
            endlockpattern = classes.EndlockPattern(**self.endlocks.to_kwargs())
        slat = classes.Slat(self.slat_type)
        return dict(endlockpattern = endlockpattern, slat = slat, slats = self.quantity)

class Endlocks(models.Model):
    endlockid = models.AutoField(primary_key = True)
    endlock_type = models.CharField(max_length = 50, choices = ENDLOCKS)
    quantity = models.PositiveIntegerField(null = True, blank = True)
    continuous = models.BooleanField(default = False, null = False)
    windlocks = models.BooleanField(default = False, null = False)

    def to_kwargs(self):
        return dict(endlock = self.endlock_type, windlocks = self.windlocks)

class BottomBar(models.Model):
    ANGLE = (
        ("D","Double Angle"),
        ("S", "Single Angle")
        )
    bottombarid = models.AutoField(primary_key  = True)
    door = models.ForeignKey("Door", models.DO_NOTHING, blank = True)
    slat_type = models.CharField(choices = SLATS, max_length = 50)
    face = models.CharField(max_length = 50, choices = FACES)
    width = models.CharField(max_length = 50, null = True, blank = True)
    angle = models.CharField(max_length = 50, choices = ANGLE)
    bottom_rubber = models.CharField(max_length = 50)
    slope_height = models.CharField(max_length = 50, null = True, blank = True)
    slope_side = models.CharField(max_length = 50, choices = HAND)

    def clean_fields(self, exclude = None):
        run_validations(self)
        return super().clean_fields(exclude)
    def validate_width(self):
        if self.width:
            return validate_measurement(self.width)
        return True
    VALIDATIONS = [("width",validate_width),
        ]

    def to_kwargs(self):
        return dict(slatweight=classes.Slat(self.slat_type), edge = self.bottom_rubber, slope = self.slope_height)

ACCESSORIES = [
    ("motorcover", "Motor Cover"),
    ("gearcover", "Gear Cover"),
    ("facia", "Facia"),
    ("foc", "FrontofMotorClip"),
    ("chainplate", "Chain Plate"),
    ("slidelocks", "Slide Locks"),
    ("pinlocks", "Pin Locks"),
    ("feederslat", "Feeder Slat"),
    ("hardware", "Hardware"),
    ("", "Other")]

class Accessory(models.Model):
    accessoryid = models.AutoField(primary_key = True)
    kind = models.CharField(max_length = 50, choices = ACCESSORIES, blank = True)
    door = models.ForeignKey("Door", models.DO_NOTHING, blank = True)
    description = models.TextField(blank = True, null = True)

class AccessoryBrackets(Brackets):
    BRACKETTYPE = [
        ("D","Drive"),
        ("C","Charge")
        ]
    door = models.ForeignKey("Door", models.DO_NOTHING,blank = True)
    type = models.CharField(max_length = 50, choices = BRACKETTYPE)

class MotorCover(Accessory):
    hand = models.CharField(max_length = 50, choices = HAND)

class GearCover(Accessory):
    hand = models.CharField(max_length = 50, choices = HAND)

class Facia(Accessory):
    length = models.CharField(max_length = 50, blank = True, null = True)
    height = models.CharField(max_length = 50, blank = True, null = True)

class FeederSlat(Accessory):
    face = models.CharField(max_length = 50, choices = FACES)
    slattype = models.CharField(max_length = 50, choices = SLATS)
    length = models.CharField(max_length = 50, blank = True, null = True)

class CustomAccessory(Accessory):
    name = models.CharField(max_length = 50)

class Hardware(Accessory):
    HARDWARE = [
        ("endlocks","Endlocks"),
        ("rivets","Rivets"),
        ("washers","Washers")
        ]
    name = models.CharField(max_length = 50, choices = HARDWARE)
    quantity = models.PositiveIntegerField(null=False,blank = False)

class HardwareEndlocks(Hardware):
    type = models.CharField(max_length = 50, choices = ENDLOCKS)
    continuous = models.BooleanField(default = False, null = False)

ACCESSORYLIST = [Accessory,AccessoryBrackets,MotorCover,GearCover,Facia,FeederSlat,CustomAccessory,Hardware,HardwareEndlocks]