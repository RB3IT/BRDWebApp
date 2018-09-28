// Stats
WIRES = {
    .1875: {
        liftrate: 11420,
        weightperinch: .0078142,
        averagetensile: 222500,
        mp_base: 143.791647518382,
        min_od: 2.75
    },
    .25: {
        liftrate: 36093,
        weightperinch: .0138916,
        averagetensile: 212500,
        mp_base: 325.520833333333,
        min_od: 2.75
    },
    .3125: {
        liftrate: 88119,
        weightperinch: .0217083,
        averagetensile: 202500,
        mp_base: 605.863683363971,
        min_od: 2.75
    },
    .375: {
        liftrate: 182724,
        weightperinch: .0312583,
        averagetensile: 197500,
        mp_base: 1021.08226102941,
        min_od: 3.75
    },
    .40625: {
        liftrate: 251546,
        weightperinch: .0366833,
        averagetensile: 191000,
        mp_base: 1255.49017214308,
        min_od: 3.75
    },
    .4375: {
        liftrate: 338448,
        weightperinch: .0425416,
        averagetensile: 190000,
        mp_base: 1559.86711090686,
        min_od: 3.75
    },
    .46875: {
        liftrate: 445807,
        weightperinch: .0488416,
        averagetensile: 185000,
        mp_base: 1868.07969037224,
        min_od: 3.75
    },
    .5: {
        liftrate: 577500,
        weightperinch: .0555666,
        averagetensile: 180000,
        mp_base: 2205.88235294118,
        min_od: 5.625
    },
    .5625: {
        liftrate: 925044,
        weightperinch: .070325,
        averagetensile: 175000,
        mp_base: 3053.55296415441,
        min_od: 5.625
    },
    .625: {
        liftrate: 1409913,
        weightperinch: .0868335,
        averagetensile: 172500,
        mp_base: 41288.4880514706,
        min_od: 5.625
    }
}

CYCLES = {
    12500: 1.055 ,
    25000:  .92  ,
    50000:  .79  ,
    100000: .68  ,
    16500: 1     ,
    }

// Helper Function
function isundefined(ref) { return typeof ref === "undefined"; };



function calculateSpring(spring) {
    /* Calculates and returns the statistics for a spring based on provided values
     
        Note on the format of this function:
            Each Calculation is formatted: "if {requirements are not undefined} [...] else throw Error [...] set spring.attr" 
            This is to accomodate additional methods of calculation and to make all the calculations uniform in execution.
     */
    // TODO: This function should be able to fill in any value provided the right data
    // is supplied, but is being written on a as-needed basis
    if (isundefined(spring.coillength)) {
        let coillength;
        if (!isundefined(spring.od) && !isundefined(spring.gauge)) {
            coillength = (spring.od - spring.gauge) * Math.PI;
        }
        else {
            throw new Error("Could not calculate spring coillength: requires od and gauge");
        };
        spring.coillength = coillength;
    };
    if (isundefined(spring.lengthuncoiled)) {
        let lengthuncoiled;
        if (!isundefined(spring.coillength) && !isundefined(spring.coils)) {
            lengthuncoiled = spring.coillength * spring.coils;
        }
        else {
            throw new Error("Could not calculate spring length uncoiled: requires coillength[req. od and gauge] and coils");
        }
        spring.lengthuncoiled = lengthuncoiled;
    };
    if (isundefined(spring.lengthcoiled)) {
        let lengthcoiled;
        if (!isundefined(spring.gauge) && !isundefined(spring.coils)) {
            lengthcoiled = spring.gauge * spring.coils;
        }
        else {
            throw new Error("Could not calculate spring length when coiled: requires guage and coils");
        }
        spring.lengthcoiled = lengthcoiled;
    };
    if (isundefined(spring.torque)) {
        let torque;
        if (!isundefined(spring.gauge) && !isundefined(spring.lengthuncoiled)) {
            let base = WIRES[spring.gauge].liftrate;
            torque = base / spring.lengthuncoiled;
        }
        else {
            throw new Error("Could not calculate spring torque: requires gauge and lengthuncoiled [req. coillength and coils]");
        }
        spring.torque = torque;
    };
    if (isundefined(spring.cyclepercentage)) {
        let cyclepercentage;
        if (!isundefined(spring.cyclerating)) {
            cyclepercentage = CYCLES[spring.cyclerating];
        }
        else {
            throw new Error("Could not calculate spring cyclepercentage: requires cyclerating.");
        }
        spring.cyclepercentage = cyclepercentage;
    };
    if (isundefined(spring.mp)) {
        let mp;
        if (!isundefined(spring.gauge) && !isundefined(spring.cyclepercentage)) {
            let mp_base = WIRES[spring.gauge].mp_base;
            mp = mp_base * spring.cyclepercentage
        }
        else {
            throw new Error("Could not calculate spring mp: requires gauge, and cyclepercentage [req. cycle rating]");
        }
        spring.mp = mp;
    };
    if (isundefined(spring.maxturns)) {
        let maxturns;
        if (!isundefined(spring.torque) && !isundefined(spring.mp)) {
            maxturns = spring.mp / spring.torque;
        }
        else {
            throw new Error("Could not calculate spring maxturns: torque [req. gauge and lengthuncoiled], and mp [req. cyclepercentage and gauge]");
        }
        spring.maxturns = maxturns;
    };

    return spring;
};