import csv
import pprint
import re
import traceback
from alcustoms import sql

db = sql.connect(r"C:\Users\J-Moriarty\Dropbox\}Python\BRD Services\BRDWebApp\db.sqlite3")
csvfile = r"C:\Users\J-Moriarty\Dropbox\}Python\BRD Services\BRDWebApp\Inventory Order.csv"
try:
    db.execute("""
UPDATE items
SET image = "inventory/images/295.0-FEnd3_16.jpg"
WHERE itemid = "295.0-FEnd3/16"
""")
    db.execute("""
UPDATE items
SET image = "inventory/images/307.0-FlatStock1-1_8.jpg"
WHERE itemid = "307.0-FlatStock1-1/8"
""")
    pprint.pprint(db.execute(f"""
SELECT itemid,image FROM items
WHERE itemid in ("295.0-FEnd3/16","307.0-FlatStock1-1/8");""").fetchall())

##    db.execute("""
##UPDATE items
##SET notes = "Cubby: C1"
##WHERE itemid = "188.0-BHX1212";
##""")
##    pprint.pprint(db.execute(f"""
##SELECT itemid,notes FROM items
##WHERE itemid = "188.0-BHX1212";""").fetchall())
##
##    db.execute("""
##UPDATE items
##SET sublocation = "Back Right"
##WHERE itemid = "19.0-AirHose";
##""")
##    pprint.pprint(db.execute(f"""
##SELECT itemid,sublocation FROM items
##WHERE itemid = "19.0-AirHose";""").fetchall())
    
    if input("Is Transfer Successful?(y/n)").lower() != "y":
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

