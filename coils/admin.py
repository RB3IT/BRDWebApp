from django.contrib import admin

from .models import SteelCoil, SteelCoilAdmin

for model,madmin in [(SteelCoil,SteelCoilAdmin),]:
    admin.site.register(model,madmin)