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
SET image = "inventory/images//" || itemid || ".jpg"
""")
    pprint.pprint(db.execute(f"""
SELECT itemid,image FROM items WHERE include""").fetchall())
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

