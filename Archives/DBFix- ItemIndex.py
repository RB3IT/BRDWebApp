import csv
import pprint
import re
import traceback
from alcustoms import sql

db = sql.connect(r"C:\Users\J-Moriarty\Dropbox\}Python\BRD Services\BRDWebApp\db.sqlite3")
try:
    def getbaditems():
        items = db.execute("""
    SELECT itemid,itemindex FROM items;
    """).fetchall()
        baditems = list()
        for itemid,itemindex in items:
            try: float(itemindex)
            except: baditems.append((itemid,itemindex))
        return baditems
    
    baditems = getbaditems()
    pprint.pprint(baditems)

    DIGITRE = re.compile("""(?P<index>^\d*)""")
    def process(itemindex):
        return float(DIGITRE.search(itemindex).group("index") + ".5")
    gooditems = [{"itemid":itemid,"itemindex":process(itemindex)} for itemid,itemindex in baditems]
    for itemupdate in gooditems:
        db.execute("""
UPDATE items
SET itemindex=:itemindex
WHERE itemid=:itemid
""",itemupdate)
        
    baditemids = "({})".format(",".join(f"'{itemid}'" for itemid,itemindex in baditems))
    pprint.pprint(
        db.execute(f"""
SELECT itemid,itemindex FROM items WHERE items.itemid IN {baditemids}""").fetchall())
    pprint.pprint(getbaditems())
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

