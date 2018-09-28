import csv
import traceback
from alcustoms import sql

db = sql.connect(r"C:\Users\J-Moriarty\Dropbox\}Python\BRD Services\BRDWebApp\db.sqlite3")
remove = "remove.csv"
locations = "location.csv"
try:
    with open (locations,'r') as f:
        locationcsv = list(csv.reader(f))
    ## Problem: Bad Steel still in Inventory
    for itemid,location in locationcsv:
        print(db.execute("""
SELECT itemid,location FROM items
WHERE itemid = :itemid;""",dict(itemid=itemid)).fetchone())


    with open(remove,'r') as f:
        removecsv = list(csv.reader(f))
    for itemid in removecsv:
        itemid = itemid[0]
        print(db.execute("""
SELECT itemid,include FROM items
WHERE itemid = :itemid;""",dict(itemid=itemid)).fetchone())
    raise Exception()
except:
    traceback.print_exc()
    db.rollback()
else:
    print('Success')
    db.commit()
finally:
    db.close()
    print('done')
