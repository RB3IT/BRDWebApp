#from django.utils.translation import gettext as _
#from django.contrib.admin import widgets as adminwidgets
#from django import forms
#from django.forms import Widget

#from core import models as coremodels

#class DateInput(forms.DateInput):
#    input_type = 'date'

#class JobInfoForm(forms.Form):
#    """ Job Info Form """
#    customer = forms.CharField(label= "Customer", choices = ())
#    customer_po = forms.CharField(label="Customer PO")
#    work_order = forms.CharField(label="Work Order Number")
#    origin_date = forms.DateField(label = "Order Date", widget = DateInput())
#    due_date = forms.DateField(label = "Due Date", widget = DateInput())

#    class Media:
#        js = ("autocomplete.js",)

#    def clean(self):
#        super().clean()
#        if not cleaned_data.get("customer"):
#            raise forms.ValidationError(
#                _("No customer provided"),
#                code = "badcustomer")

#        ## If order_date or due_date did not validate above, they won't exist in cleaned_data
#        start,stop = self.cleaned_data.get("order_date"), self.cleaned_data.get("due_date")
        
#        ## Per above, both values were properly validated
#        if start and stop:
#            ## Invalid order date/order due date combination
#            if start > stop:
#                raise forms.ValidationError(
#                    _(f"Order Date {start.strftime('%d/%m/%Y')} is after Due Date {stop.strftime('%d/%m/%Y')}"),
#                    code='badtimes',)