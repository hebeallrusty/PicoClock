import math

def Hrs(DecimalHrs,OmitSec = True):
    HRS = math.floor(DecimalHrs)
    MIN = math.floor((DecimalHrs - HRS) * 60)
    SEC = math.floor(((((DecimalHrs - HRS) * 60)) - MIN) * 60)

    if OmitSec == True:
        # TODO - rounding logic; meantime truncate
        #if (SEC >= 30) and (MIN == 59): # round up to the hour
        #    HRS = +1
        #    MIN += 1
        return((HRS,MIN))

    else:   
        return((HRS,MIN,SEC))
