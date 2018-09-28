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
SET itemindex = 12.05
WHERE itemid = "274.0-BottomRubber";
""")
    db.execute("""
UPDATE items
SET sublocation = "Back Right"
WHERE itemid = "274.0-BottomRubber";
""")
    pprint.pprint(db.execute(f"""
SELECT itemid,itemindex,sublocation FROM items
WHERE itemid = "274.0-BottomRubber";""").fetchall())
    
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

