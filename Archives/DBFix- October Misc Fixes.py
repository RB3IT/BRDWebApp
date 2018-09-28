import datetime
import pprint
import traceback
import sqlite3 as sql

from BRDSolution.inventory import constants

db = sql.connect(r"C:\Users\J-Moriarty\Dropbox\BRD Services\BRDWebApp\db.sqlite3")
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d
db.row_factory = dict_factory

def separator():
    print("-------------")

try:
    db.execute("""UPDATE "items" SET itemindex = 250.5 WHERE itemid = "275.0-4P1";""")
    items = db.execute("""SELECT description,itemid,itemindex FROM "items" WHERE itemindex > 249 AND itemindex < 260 ORDER BY itemindex""").fetchall()
    print('Updated Item Index for 4" Pipe Casting')
    pprint.pprint(items)

    separator()

    db.execute("""UPDATE "items" SET notes = "Cubby: C4" WHERE itemid = "182.0-BCR1212";""")
    db.execute("""UPDATE "items" SET notes = "Cubby: E4" WHERE itemid = "239.0-PRX3830";""")
    items = db.execute("""SELECT description,itemid,notes FROM "items" WHERE itemid in ("182.0-BCR1212","239.0-PRX3830");""").fetchall()
    print("Updated Item Location Notes")
    pprint.pprint(items)

    separator()
    
    db.execute("""UPDATE "items" SET location = "Bristol & Pipe", sublocation = "Center Rack: Right & Steel Rack" WHERE itemid = "303.0-AI2218G";""")
    items = db.execute("""SELECT description,itemid,location,sublocation FROM "items" WHERE itemid = "303.0-AI2218G";""").fetchall()
    print("Updated 2x2 Location")
    pprint.pprint(items)

    separator()
    
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

