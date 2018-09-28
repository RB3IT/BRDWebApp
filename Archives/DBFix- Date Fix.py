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

try:
    for table in ["costs","inventory","stock"]:
        rows = db.execute(f"""
SELECT id,date FROM {table};
""").fetchall()
        if not rows: raise Exception(" No Rows ")
        updaterows = []
        for row in rows:
            try: row['date'] = datetime.datetime.strptime(row['date'],"%Y-%m-%d %H:%M:%S")
            except: pass
            else: updaterows.append(row)
        print(f"Rows to update in {table}: {len(updaterows)} out of {len(rows)}")
        if updaterows:
            for row in updaterows: row['date'] = row['date'].strftime(constants.DATEFORMAT)
            db.executemany(f"""
            UPDATE {table}
            SET date = :date
            WHERE id = :id
            """,updaterows)

            ids = ", ".join(str(row['id']) for row in updaterows)
            pprint.pprint(db.execute(f"""
            SELECT id, date
            FROM {table}
            WHERE id in ({ids});""",
                                     dict(ids = ids)).fetchall())
    
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

