import csv
import pprint
import traceback
from alcustoms import sql

db = sql.connect(r"C:\Users\J-Moriarty\Dropbox\}Python\BRD Services\BRDWebApp\db.sqlite3")
try:
    pprint.pprint(db.execute("""
SELECT itemid,sums FROM inventory
WHERE inventory.notes!=null;""").fetchall())
    db.execute("""
UPDATE inventory
SET sums = notes;
""")
    db.execute("""
UPDATE inventory
SET notes = '';
""")
    pprint.pprint(db.execute("""
SELECT itemid,notes FROM inventory
WHERE inventory.notes!=null;""").fetchall())
    if input("Is Transfer Successful?(y/n)") != "Y":
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

