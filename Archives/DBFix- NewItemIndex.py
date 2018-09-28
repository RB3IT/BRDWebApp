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
    for item in items:
        try:
            item['itemindex'] = float(item['itemindex'])
        except:
            item['itemindex'] = 100000000000
    items = sorted(items,key = lambda item:item['itemindex'])
    updates = [{'itemid':item['itemid'],'itemindex':item['itemindex']} for item in items]
    for itemupdate in updates:
        db.execute("""
UPDATE items
SET itemindex=:itemindex
WHERE itemid=:itemid
""",itemupdate)
    pprint.pprint(
        sorted(
            db.execute(f"""
SELECT description,itemindex FROM items WHERE include = 1""").fetchall(),
            key = lambda item: item[1])
        )
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

