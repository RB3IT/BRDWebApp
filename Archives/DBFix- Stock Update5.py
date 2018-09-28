import datetime
import pprint
import traceback
import sqlite3 as sql

db = sql.connect(r"C:\Users\J-Moriarty\Dropbox\BRD Services\BRDWebApp\db.sqlite3")
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d
db.row_factory = dict_factory

try:
    db.execute("""
    UPDATE items
    SET itemindex = 1000
    WHERE itemid in (
        SELECT itemid
        FROM stock
        WHERE date = :date
    );
    """,dict(date = datetime.datetime(2015,12,31), olddate = datetime.datetime(2017,1,1)))
    
    pprint.pprint(db.execute(f"""
SELECT items.itemid, items.itemindex
FROM items
LEFT JOIN stock ON stock.itemid = items.itemid
WHERE date = :date;""",
                             dict(date = datetime.datetime(2015,12,31), olddate = datetime.datetime(2017,1,1))).fetchall())
    
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

