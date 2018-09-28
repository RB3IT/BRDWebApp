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
INSERT INTO stock (itemid,date,include) SELECT itemid,:date,1 FROM items;
""",dict(date = datetime.datetime(1990,1,1)))
    db.execute("""
INSERT INTO stock (itemid,date,include) SELECT itemid,:date,0 FROM items WHERE items.include = 0;
""",dict(date = datetime.datetime(2017,4,1)))
    pprint.pprint(db.execute(f"""SELECT * FROM stock;""").fetchall())
    
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

