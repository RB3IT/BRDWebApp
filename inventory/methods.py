## Builtin
import datetime
import re
## Backend
from django.db import models as djangomodels
## Custom Module
from alcustoms import methods as almethods
## This Module
from . import models
from . import subclasses
## This class is imported by excelmethods,views. DO NOT IMPORT!
## Sister Module
from BRDSolution.inventory import constants

def itermonths(start,end):
    """ (Generator) Iterate over a range between start Datetime's Month/Year to end Datetime's Month/Year, returning each itermediate Month/Year """
    ## TODO: Remove this autosorting, use op.lt/op.gte for while loop, create almethods.getfirstofpreviousmonthdatetime
    start,end = sorted([start,end])
    ## For each Month/Year Datetime between Start and End (Inclusive)
    while start <= end:
        ## Return Current Datetime (Start, Start + 1 Month, Start + 2 Months, etc)
        yield start
        ## Advance Current Datetime by 1 Month
        start = almethods.getfirstofnextmonthdatetime(start.year,start.month)

def validatedate(month,year):
    if isinstance(month,str):
        try:
            month = constants.MONTHLIST.index(month)
        except:
            try:
                month = int(month)
            except:
                return False
    month,year = int(month),int(year)
    if (1<=month<=12 or month in constants.MONTHLIST) and  1900<=int(year)<=2100:
        if month in constants.MONTHLIST: month = constants.MONTHLIST.index(month)
        return datetime.datetime(year=year,month=month,day=1)
    return False

def validatedatetime(date):
    if datetime.datetime(year=2100,month=12,day=31) > date > datetime.datetime(year=1900,month=1,day=1):
        return True

NUMBERRE = re.compile("(?P<number>\d+)")
def nonnumbersort(invite):
    """ For Sorting Inventory Items with ItemIndex that is non-number (i.e.- 340A) """
    try:
        return int(invite.itemindex)
    except:
        search = NUMBERRE.search(invite.itemindex)
        if not search: return 0
        return int(search.group("number"))

def getincludeditems(month):
    """ Returns a QuerySet of Items which have the included Flag prior to the given month """
    currentstock = models.Stock.objects.filter(date__lte=month)\
                                        .annotate(date=djangomodels.Max("date"))\
                                        .filter(include = True)
#    include= models.Stock.objects.raw("""
#    SELECT *
#    FROM (
#        SELECT "stock"."id","stock"."itemid",MAX("stock"."date") as "newest", "stock"."include"
#        FROM "stock"
#        WHERE "stock"."date" <= "{month}"
#        GROUP BY "stock"."itemid" HAVING MAX("stock"."date") = (MAX("stock"."date"))
#        )
#    WHERE include = 1;
#""".format(month = month.strftime(constants.DATEFORMAT)))
    include = [stock.itemid.itemid for stock in include]
    out = models.Items.objects.filter(itemid__in=include).order_by('itemindex','description')
    return out

def getlastdecember(month):
    """ Returns a datetime representing the most recent, previous December (not including supplied month)

    month should be a datetime to start from; if it is December, then the previous December will be supplied.
    """
    ## ... This seemed like it would be more difficult...
    december = datetime.datetime(year = month.year - 1, month = 12, day = 1)
    return december

def getinventorybymonth(month):
    """ Gets a list of all Items from the Database that have the .included flag set and updates them with the appropriate quantities.

    month should be a datetime object.
    reutrns a list of subclasses.InventoryItem objects.
    """
    ## Get all Included Items
    itemlist = getincludeditems(month)
    ## Get all Inventory Items
    inventorylist = {obj.itemid:obj for obj in models.Inventory.objects.filter(date = month).order_by("itemid__itemindex","itemid__description")}
    ## Crossreference Items with Inventory, transfering over any inventory counts
    output = list()
    for item in itemlist:
        ## Creating a special Container Class which includes attributes of both Items and Inventory
        invite = subclasses.InventoryItem(itemid=item.itemid,itemindex = item.itemindex, date=month,description=item.description,
                                                         location=item.location, sublocation = item.sublocation, unitsize=item.unitsize,
                                                         notes=item.notes, image = item.image)
        ## If Item in Inventory List, update it's quantity
        if item in inventorylist:
            invite.quantity = inventorylist[item].quantity
        ## Add to output
        output.append(invite)

    ## Item.itemindex is not always a number
    output = sorted(output,key =  nonnumbersort)
    return output

def getcostforinventory(*inventory):
    """ (Mutating) Gets the most recent cost for each Item in an inventory and sets it on the InventoryItem

    Accepts positional arguments of items (objects which have a .itemid, and datetime .date attribute).
    Returns None (mutates the item in-place by setting .cost attribute).
    """
    for item in inventory:
        lastday = almethods.getlastdaydatetime(year = item.date.year, month = item.date.month)
        costs = models.Costs.objects.filter(itemid=item.itemid,date__lte=lastday)
        if not costs: item.cost = 0
        else:
            ## QuerySets do not support Negative Indexing
            item.cost = list(costs)[-1].cost
    return