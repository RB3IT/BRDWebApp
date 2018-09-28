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
    UPDATE stock SET date = :date WHERE date = :olddate;
    """,dict(date = datetime.datetime(2015,12,31), olddate = datetime.datetime(2017,1,1)))
    
    pprint.pprint(db.execute(f"""SELECT * FROM stock WHERE date = :date;""",
                             dict(date = datetime.datetime(2015,12,31), olddate = datetime.datetime(2017,1,1))).fetchall())
                  
    pprint.pprint(db.execute(f"""SELECT * FROM stock WHERE date = :olddate;""",
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

