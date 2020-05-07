from django.contrib import admin
from . import models

# Register your models here.
for model,madmin in [(models.ShoppingItems, models.ShoppingItemsAdmin),
                     (models.ShoppingListItem, models.ShoppingListItemAdmin)]:
    admin.site.register(model,madmin)