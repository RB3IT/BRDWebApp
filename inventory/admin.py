from django.contrib import admin

from .models import Items,Costs,Inventory,Stock, StockWidgets\
                    ,ItemsAdmin,CostsAdmin,InventoryAdmin,StockAdmin, StockWidgetsAdmin

for model,madmin in [(Items,ItemsAdmin),(Costs,CostsAdmin),(Inventory,InventoryAdmin),(Stock,StockAdmin),(StockWidgets, StockWidgetsAdmin),]:
    admin.site.register(model,madmin)