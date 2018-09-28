
class InventoryItem():
    def __init__(self,itemid,itemindex, description,location,sublocation,unitsize,date,cost = 0, quantity=None,sums = None, notes = None, usernotes = None, image = None):
        self.itemid = itemid
        self.itemindex = itemindex
        self.description = description
        self.location = location
        self.sublocation = sublocation
        self.unitsize = unitsize
        self.date=date
        self._quantity = quantity
        self.cost = cost
        self.sums = sums
        self.notes = notes
        self.usernotes = usernotes
        self.image = image
    @property
    def quantity(self):
        if self._quantity is None: return self._quantity
        return f"{float(self._quantity):.2f}"

    @quantity.setter
    def quantity(self,value):
        self._quantity = value

    @property
    def total(self):
        return self.cost * self.quantity