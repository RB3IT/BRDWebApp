import csv
import datetime
import pprint
import traceback
import sqlite3 as sql
from BRDSolution.inventory import constants

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

db = sql.connect(r"C:\Users\J-Moriarty\Dropbox\BRD Services\BRDWebApp\db.sqlite3")
db.row_factory = dict_factory
try:
    cur = db.execute("""
    SELECT *
    FROM costs
    WHERE :date < date < :date2;
""",dict(date = datetime.datetime(2017,3,1),date2=datetime.datetime(2017,4,1)))
    pprint.pprint(cur.fetchall())
finally:
    db.rollback()
    db.close()
    print('done')

