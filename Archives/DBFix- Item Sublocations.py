import csv
import pprint
import re
import traceback
from alcustoms import sql

db = sql.connect(r"C:\Users\J-Moriarty\Dropbox\}Python\BRD Services\BRDWebApp\db.sqlite3")
csvfile = r"C:\Users\J-Moriarty\Dropbox\}Python\BRD Services\BRDWebApp\Inventory Order.csv"
try:
    with open(csvfile,'r') as f:
        reader = csv.DictReader(f)
        items = list(reader)
    updates = [{'itemid':item['itemid'],'sublocation':item['sublocation']} for item in items]
    for itemupdate in updates:
        db.execute("""
UPDATE items
SET sublocation=:sublocation
WHERE itemid=:itemid
""",itemupdate)
    pprint.pprint(db.execute(f"""
SELECT description,sublocation FROM items WHERE include""").fetchall())
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

