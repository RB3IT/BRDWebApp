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

UPDATEITEMS = [
  {
    "description": "Air Wave 10 Safety edge switch",
    "itemid": "1.0-AW-10"
  },
  {
    "description": "3-36 Multi-Purpose Lubricant, 11oz Aerosol",
    "itemid": "125.0-03005"
  },
  {
    "description": "Knock'er Loose - Penetraring Solvent",
    "itemid": "128.0-03020"
  },
  {
    "description": "Power Lube with Teflon, 16oz Aerosol",
    "itemid": "131.0-03045"
  },
  {
    "description": "White Lithium Grease, 16oz Aerosol",
    "itemid": "134.0-03080"
  },
  {
    "description": "Heavy Duty Degreaser, 20oz Aerosol  ",
    "itemid": "136.0-03095"
  },
  {
    "description": "Gray, Rust Proof Primer, 15oz Aerosol",
    "itemid": "150.0-18150"
  },
  {
    "description": "Mechanix Orange Hand Cleaner, 1 Gallon Bottle with Pump.",
    "itemid": "153.0-SL1719"
  },
  {
    "description": "1/2\" Drill Bit, KFD Series",
    "itemid": "157.0-DBKFD1/2"
  },
  {
    "description": "1/4\" Drill Bit, KFD Series",
    "itemid": "158.0-DBKFD1/4"
  },
  {
    "description": "1/8\" Drill Bit, KFD Series",
    "itemid": "159.0-DBKFD1/8"
  },
  {
    "description": "3/16\" Drill Bit, KFD Series",
    "itemid": "170.0-DBKFD3/16"
  },
  {
    "description": "5/16\" Drill Bit, KFD Series",
    "itemid": "173.0-DBKFD5/16"
  },
  {
    "description": "7/32\" Drill Bit, KFD Series",
    "itemid": "177.0-DBKFD7/32"
  },
  {
    "description": "Control Station, 3 Button, Interior",
    "itemid": "18.0-CS-PBS3"
  },
  {
    "description": "3/8\"-16 x 2\" Hex Head Tap Bolt, Grade 2",
    "itemid": "194.0-BHX3820"
  },
  {
    "description": "3/8\"-16 x 3\" Hex Head Tap Bolt, Grade 2",
    "itemid": "195.0-BHX3830"
  },
  {
    "description": "5/16\"-18 x 1\" Hex Head Tap Bolt",
    "itemid": "196.0-BHX5610"
  },
  {
    "description": "Air Wave 10 Safety edge switch in a NEMA 4x Enclosure",
    "itemid": "2.0-AW-12"
  },
  {
    "description": "#10 SAE Flat Washer (5 Pound Box)",
    "itemid": "206.0-WFS10"
  },
  {
    "description": "1/2\" Flat Washers, USS (5 Pound Box)",
    "itemid": "208.0-WFX12"
  },
  {
    "description": "1/4\" Flat Washer",
    "itemid": "209.0-WFX14"
  },
  {
    "description": "18-2 Coil Cord",
    "itemid": "21.0-CoilCord"
  },
  {
    "description": "5/16\" Flat Washer, USS",
    "itemid": "211.0-WFX56"
  },
  {
    "description": "Cord Reel, 18-3, 20\"",
    "itemid": "22.0-CordReel"
  },
  {
    "description": "3/8\" x 3-1/2\" Round Head Steel Rivet",
    "itemid": "235.0-MRR3832"
  },
  {
    "description": "1/4\" x 1-1/2\" Spring Pin (Roll Pin)",
    "itemid": "236.0-PRX1412"
  },
  {
    "description": "Artisan Timer",
    "itemid": "24.0-Timer"
  },
  {
    "description": "5/16\" x 1-1/2\" Spring Pin (Roll Pin)",
    "itemid": "240.0-PRX5612"
  },
  {
    "description": "5/16\" x 2\" Spring Pin (Roll Pin)",
    "itemid": "241.0-PRX5620"
  },
  {
    "description": "5/16\" x 2-1/2\" Spring Pin (Roll Pin)",
    "itemid": "242.0-PRX5622"
  },
  {
    "description": "             x            Rolling Steel Service Door, Non-Weather Seal",
    "itemid": "252.0-RD-1209"
  },
  {
    "description": "             x            Rolling Steel Service Door, Non-Weather Seal",
    "itemid": "253.0-RD-1210"
  },
  {
    "description": "             x            Rolling Steel Service Door, Non-Weather Seal",
    "itemid": "254.0-RD-1211"
  },
  {
    "description": "             x            Rolling Steel Service Door,  Non-Weather Seal",
    "itemid": "255.0-RD-1212"
  },
  {
    "description": "             x            Rolling Steel Service Door,  Non-Weather Seal",
    "itemid": "256.0-RD-1213"
  },
  {
    "description": "             x            Rolling Steel Service Door Non-Weather Seal",
    "itemid": "257.0-RD-1214"
  },
  {
    "description": "Cookson Stamped Flat Endlocks, #5",
    "itemid": "292.0-CooksonEnd#5"
  },
  {
    "description": "Cookson Windlocks, #5, 2-115-07-P",
    "itemid": "293.0-CooksonWind#5"
  },
  {
    "description": "Limit Nut, Nylon",
    "itemid": "30.0-LimitNut"
  },
  {
    "description": "3-1/2\" x 3-1/2\" x 1/4\" Angle Iron, 20\" long",
    "itemid": "306.0-AI353514"
  },
  {
    "description": "3/16\" x 4\" x 20\", Flat Stock",
    "itemid": "309.0-FlatStock4-3/16"
  },
  {
    "description": "Limit Switch, Double Up.",
    "itemid": "31.0-LimitSwitchDBL"
  },
  {
    "description": "5.225 wide x 22-Gauge Steel (Band Spring)",
    "itemid": "317.0-SlatSteel5255"
  },
  {
    "description": "5.280 wide x 20-Gauge Steel (BRD & NY Slat)",
    "itemid": "318.0-SlatSteel5280"
  },
  {
    "description": "5.282 wide x 22-Gauge Gray Prime Steel",
    "itemid": "319.0-SlatSteel5282"
  },
  {
    "description": "Limit Switch, DPDT(Special Use)",
    "itemid": "32.0-LS-DPDT"
  },
  {
    "description": "5.340 wide x 20-Gauge Steel (Crown)",
    "itemid": "320.0-SlatSteel5340"
  },
  {
    "description": "Grille Rods, 25\"",
    "itemid": "328.0-GrilleRods"
  },
  {
    "description": "Limit Switch, SPST (Open/Close)",
    "itemid": "33.0-LS-SPST"
  },
  {
    "description": "Crown Feeder Slat",
    "itemid": "339.0-CrownFeeder"
  },
  {
    "description": "6013 Band Spring",
    "itemid": "352.0-6013"
  },
  {
    "description": "10\" Spring Box",
    "itemid": "360.0-Spring Box"
  },
  {
    "description": "V Cup Pipe Holder",
    "itemid": "361.0-VCup"
  },
  {
    "description": "Adaptor Rail, 8\"2\"",
    "itemid": "362.0-ADPRAIL08"
  },
  {
    "description": "Adaptor Rail, 10\"2\"",
    "itemid": "363.0-ADPRAIL10"
  },
  {
    "description": "Adaptor Rail, 12\"2\"",
    "itemid": "364.0-ADPRAIL12"
  },
  {
    "description": "Adapter Rail - 14\"2\"",
    "itemid": "365.0-ADPRAIL14"
  },
  {
    "description": "Adapter Rail - 16\"2\"",
    "itemid": "366.0-ADPRAIL16"
  },
  {
    "description": "Adaptor Rail, 24\"6\"",
    "itemid": "367.0-ADPRAIL24"
  },
  {
    "description": "Steel Door Bottom Astragal",
    "itemid": "368.0-Astragal"
  },
  {
    "description": "Cable Keepers (Pair)",
    "itemid": "376.0-CableKeepers"
  },
  {
    "description": "Chain Hoist Kit",
    "itemid": "377.0-ChainHoist"
  },
  {
    "description": "14\" 2\" x 24\" Pan, 24 Gauge, White",
    "itemid": "398.0-PAN142W24"
  },
  {
    "description": "Bottom Rubber Retainer Angle, 7\" 5\"",
    "itemid": "401.0-RA08"
  },
  {
    "description": "Bottom Rubber Retainer Angle, 14\" 0\"",
    "itemid": "404.0-RA14"
  },
  {
    "description": "Aluminum SRP Retainer",
    "itemid": "407.0-SRP-Retainer"
  },
  {
    "description": "Break Solenoid, 120v",
    "itemid": "42.0-Solenoid120"
  },
  {
    "description": "Break Solenoid, 230v",
    "itemid": "43.0-Solenoid230"
  },
  {
    "description": "Transformer, Single Phase",
    "itemid": "44.0-Transformer-1"
  },
  {
    "description": "Transformer, 3 Phase",
    "itemid": "45.0-Transformer-3"
  },
  {
    "description": "Trolly Arm Assembly (Both Parts)",
    "itemid": "46.0-TrollyArm"
  },
  {
    "description": "Trolly Rails, 16\" long",
    "itemid": "47.0-TrollyRail16"
  },
  {
    "description": "Gearhead Trolly, 1 HP, 460, 3 phase, 24\" rails  S/N:",
    "itemid": "49.0-GT-104-T-24"
  },
  {
    "description": "Hoist - Belt Operator, 1/3 hp, 230v, 1 phase  S/N:",
    "itemid": "50.0-H-34-T-16"
  },
  {
    "description": "Hoist - Belt Operator, 1/2 hp, 230v, 1 phase  S/N:",
    "itemid": "52.0-H-5021-L3R"
  },
  {
    "description": "Hoist - Belt Operator, 1/2 hp, 230v, 3 phase  S/N:",
    "itemid": "53.0-H-5023-L3R"
  },
  {
    "description": "Hoist - Belt Operator, 3/4 hp, 115v, 1 phase  S/N:",
    "itemid": "55.0-H-71-T-16"
  },
  {
    "description": "Hoist - Belt Operator, 3/4 hp, 230v, 1 phase  S/N:",
    "itemid": "56.0-H-72-T-16"
  },
  {
    "description": "Hoist - Belt Operator, 3/4 hp, 230v, 3 phase  S/N:",
    "itemid": "57.0-H-73-T-16"
  },
  {
    "description": "Hoist - Belt Operator, 3/4 hp, 460v, 3 phase  S/N:",
    "itemid": "58.0-H-74-T-16"
  },
  {
    "description": "Gearhead Operator, 1 hp, 230v, 1 phase  S/N:",
    "itemid": "61.0-MG-102-T-16 / GH1021-L4R"
  },
  {
    "description": "Gearhead Operator, 1hp, 230v, 3 phase  S/N:",
    "itemid": "62.0-GH1023-L3"
  },
  {
    "description": "Gearhead Operator, 1-1/2 hp, 115v, 1 phase  S/N:",
    "itemid": "64.0-MG-151-T-16"
  },
  {
    "description": "Gearhead Operator, 2hp, 230v, 3ph  S/N:",
    "itemid": "65.0-MG-203-T-16"
  },
  {
    "description": "Gearhead Operator, 2 hp, 460v, 3 phase  S/N:",
    "itemid": "66.0-MG-204-T-16"
  },
  {
    "description": "Gearhead Operator, 3 hp, 460v, 3 phase  S/N:",
    "itemid": "67.0-MG-304-T-16"
  },
  {
    "description": "Gearhead Operator, 1/2 hp, 230v, 1 phase  S/N:",
    "itemid": "69.0-MG-52-T-16"
  },
  {
    "description": "Gearhead Operator, 1/2 hp, 230v, 3 phase  S/N:",
    "itemid": "70.0-MG-53-T-16"
  },
  {
    "description": "Trolly Operator, 1/2 hp, 230v, 1 phase, 16\" Rails  S/N:",
    "itemid": "73.0-T-52-T-16"
  },
  {
    "description": "Trolly Operator, 1/2 hp, 230v, 3 phase, 16\" Rails  S/N:",
    "itemid": "74.0-T-53-T-16"
  },
  {
    "description": "Trolly Operator, 1/2 hp, 460v, 3 phase, 16\" Rails  S/N:",
    "itemid": "75.0-T-54-T-16"
  }
]

try:
    for item in UPDATEITEMS:
        db.execute("""
    INSERT INTO stock (itemid,date,include) VALUES (:itemid,:date,0);
    """,dict(itemid=item['itemid'],date = datetime.datetime(2017,1,1)))
    pprint.pprint(db.execute(f"""SELECT * FROM stock WHERE date = :date;""",
                             dict(date = datetime.datetime(2017,1,1))).fetchall())
    
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

