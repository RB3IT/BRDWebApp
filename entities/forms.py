from django import forms
from . import models
from . import widgets

class CompanyForm(forms.Form):

    company_name = forms.CharField(label='Name', max_length=100)

    company_role = forms.MultipleChoiceField(choices = models.CompanyRole.ROLES)

