from django.shortcuts import render
from django.views import generic as dviews
import django.http

from . import models
import doors.models

# Create your views here.
class Home(dviews.TemplateView):
    """ Home View """
    template_name = "core/home.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


API_COMPANY_VALIDKEYS = ["search","po"]
def API_company(request):
    """ API hub for companies """
    query = request.GET
    if any(key for key in query if key not in API_COMPANY_VALIDKEYS):
        #print([(key,key not in API_COMPANY_VALIDKEYS) for key in query])
        return django.http.HttpResponseBadRequest("Invalid query")
    if "search" in query:
        return API_companysearch(request)
    elif "po" in query:
        return API_companypo(request)
    return django.http.Http404()

def API_companysearch(request):
    """ Actual backend for parsing company search request (from API_company) """
    company = request.GET.get("search")
    company = str(company).strip()
    results = models.Company.objects.filter(name__icontains = company)
    results = [[company.pk,company.name] for company in results]
    return django.http.JsonResponse({"success":True,"results":results})

def API_companyPO(request):
    """ Actual backend for parsing company po search request (from API_company) """
    company = request.GET.get("po")
    search = request.GET.get("po_search")
    company = models.Company.objects.get(pk = company)
    if not company: return django.http.HttpResponseBadRequest("Invalid company ID")
    pos = doors.models.Order.objects.filter(customer_po__icontains = company)
    results = [po.customer_po for po in pos]
    return django.http.JsonResponse({"success":True,"results":results})