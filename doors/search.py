## Builtin
import datetime
import re
## Backend
from django.db.models import Q
## This Module
from . import models
## Custom Module
from alcustoms import delimparser, measurement

TOKENIZER = delimparser.Tokenizer()

SEARCHDATERE = re.compile(r"""
^(?P<equality>([<>=])(?!\2)[<>=]?)?
(?P<date>
  \d+ ([/-])
  \d+ \4
  \d+
)
""", re.IGNORECASE|re.VERBOSE)

OBJECTSEARCHRE = re.compile(r"""
^(?P<modifiers>
    ([<>=])(?!\2)[<>=]? |
    [~]
)
""", re.IGNORECASE|re.VERBOSE)

def stripmatch(input,match,group = 0):
    """ Strips the match from the front of the string and any additional whitespace at both ends (via strip()) """
    return input.replace(match.group(group),"",1).strip()

BASICTEXTSEARCH = {"customer":"customer__name",
                   "customer_po":"customer_po",
                   "po":"customer_po",
                   "work_order":"work_order",
                   "wo":"work_order",
                   "description":"description"}

DATEFIELDS = {
    "date":"date",
    "entered":"date",
    "origin":"origin_date",
    "origin_date":"origin_date",
    "due":"due_date",
    "due_date":"due_date",
    "description":"description",
    "descr":"description",
    }

## Objects require additional parsing, so there is no direct lookup functionality
OBJECTFIELDS = {
    "door":models.Door,
    "hood":models.Hood,
    "pipe":models.Pipe,
    "springs":models.Spring,
    "tracks":models.Tracks,
    "curtain":models.Slats,
    "bottombar":models.BottomBar,
    "accessories":None}

EQUALITYLOOKUP = {">=":"__gte","=>":"__gte","<=":"__lte","=<":"__lte",">":"__gt","<":"__lt","=":"","~":"__icontains"}

def hasfield(model,field):
    try: model._meta.get_field(field)
    except: return False
    return True

def _get_fklist(model,query,fk):
    return model.objects.filter(**query).values_list(fk, flat = True)

def _get_parentobj(parent,model,query,fk):
    """ Filter the given model by the query, then extract it's parent's fk (as defined) and use that to return a QuerySet of its Parent Objects """
    return model.objects.filter(pk__in = 
                                _get_fklist(model,query,fk)
                                )

def _execute_fields(searchfields):
    """ Runs the actual database search for the given SearchFields """
    ## Catching notiterable instead of check for iterability
    try:
        if not all(isinstance(field,delimparser.Field) for field in searchfields):
            raise TypeError("Invalid search fields")
    except:
        raise TypeError("Invalid search fields")

    output = []
    for field in searchfields:
        result = None
        if field.neg:
            attr = "exclude"
        else:
            attr = "filter"
        name = field.kind.replace(" ","_").lstrip('"').rstrip('"')
        if name in BASICTEXTSEARCH:
            q = BASICTEXTSEARCH[name]
            if not field.value: continue
            value = field.value.kind
            if not value: continue
            result = getattr(models.Order.objects,attr)(**{q+"__icontains":value})
        elif name in DATEFIELDS:
            q = DATEFIELDS[name]
            value = field.value.kind
            if not value: continue
            qrquery = SEARCHDATERE.search(value)
            if not qrquery:
                continue
            matchtype = ""
            if qrquery.group("equality"):
                qquery = stripmatch(field.value.kind,qrquery,group = "equality")
                equals = qrquery.group("equality")
                if equals in EQUALITYLOOKUP:
                    matchtype = EQUALITYLOOKUP[equals]
                ## Ignore on invalids
                else:
                    continue
            else:
                qquery = field.value.kind
            ## Try parsing date
            try:
                qquery = datetime.datetime.strptime(qquery,"%m/%d/%Y")
            except:
                try:
                    qquery = datetime.datetime.strptime(qquery,"%d/%m/%Y")
                ## give up at this point
                except:
                    continue
            result = getattr(models.Order.objects,attr)(**{q+matchtype:qquery})
        elif name in OBJECTFIELDS:
            ## Can't do anything without a value
            if not field.value:
                continue
            model = OBJECTFIELDS[name]
            val = field.value
            field = val.kind
            if not hasfield(model,field): continue
            search = val.value
            if not search: continue
            search = search.kind
            if not search: continue
            search = search.strip('"')
            modresult = OBJECTSEARCHRE.match(search)
            matchtype = ""
            if modresult:
                search = stripmatch(search,modresult,"modifiers")
                matchtype = modresult.group("modifiers")
                if matchtype in EQUALITYLOOKUP:
                    matchtype = EQUALITYLOOKUP[matchtype]

            if hasattr(model,"MEASUREMENTFIELDS") and field in model.MEASUREMENTFIELDS:
                search = measurement.convertmeasurement(search)
            if name != "door":
                if name == "spring":
                    search = _get_fklist(model,{field+matchtype:search},"pipe")
                    model = models.Pipe
                    field = "pk"
                    matchtype = "__in"
                doors = _get_parentobj(models.Door,model,{field+matchtype:search},"door")
            else:
                doors = model.objects.filter(**{field+matchtype:search})
            
            result = getattr(models.Order.objects,attr)(pk__in = 
                                                 doors.values_list("order",flat = True)
                                                 )            
        else:
            result = models.Order.objects.filter(
                Q(customer__name__icontains=field.kind) |
                Q(customer_po__icontains=field.kind) |
                Q(work_order__icontains=field.kind) |
                Q(description__icontains=field.kind))
        if result:
            output.append(result.exclude(_delete_flag = True))
    return output

def parse(query):
    """ Parses an order search query """
    fields = TOKENIZER(query)
    if isinstance(fields,delimparser.Field):
        fields = [fields,]
    results = _execute_fields(fields)

    if results:
        start,results = results[0],results[1:]
        results = start.intersection(*results)
    return results