# Calculate the rise and set times of a location
#
# Requires:
#    YEAR: int value of the year
#    MONTH: int value of the month
#    DAY: int value of the day
#    longitude: decimal value of longitude
#    latiude: decimal value of latitude
#    offset: offset to be applied for local time - default is UTC
#
# Call SunTimes(YEAR,MONTH,DAY, latitude, longitude, offset (optional))
#
# Produces a dictionary of Tuples with rise and set times; all times are in decimal time - i.e. 07:15 = 7.25; 07:45 = 7.75 etc
#
# Method used is from:
# Almanac for Computers, 1990
# published by Nautical Almanac Office
# United States Naval Observatory
# Washington, DC 20392

import math

def DayOfYear(YEAR,MONTH,DAY):
    
    # calculates the day of the year and return the day number
    
    N1 = math.floor(275 * MONTH / 9)
    N2 = math.floor((MONTH + 9) / 12)
    N3 = (1 + math.floor((YEAR - 4 * math.floor(YEAR / 4) + 2) / 3))
    return(N1 - (N2 * N3) + DAY - 30)
    

def SunTimes(YEAR, MONTH, DAY, latitude, longitude, offset = 0):
    
    zenith = [90 + 50/60, 96, 102, 108, 84]
    zenith_labels = ['Official','Civil','Nautical','Astronomical','Golden']
    # convert zenith's for ease of calcs further on
    zenith = [math.cos(math.radians(i)) for i in zenith]
    #zenith = [0.10472,-0.01454, -0.10453, -0.20791, -0.30902]
    # golden 84 deg approx 0.10472
    # official 90 deg 50' approx -0.01454
    # civil / dusk/dawn 96 deg approx -0.10453
    # nautical 102 deg approx -0.20791
    # astronomical 108 deg approx -0.30902
    # noon 0 deg
    
    # 1 calculate the day of the year
    N = DayOfYear(YEAR,MONTH,DAY)
    
    # 2 convert the logitude to hour value and calculate an approximate time
    
    lngHour = longitude / 15
    
    # create list for rise and set; t = [rise, set]
    
    t = [0] * 2
    
    # add in the relevant calculations for both rise and set
    
    t[0] = N + ((6 - lngHour) / 24)
    t[1] = N + ((18 - lngHour) / 24)
    
    # 3 calculate the Sun's Mean Anomaly
    
    M = [(0.9856 * i) - 3.289 for i in t]
    
    # 4 calculate the Sun's true longitude
    # calcs need to use Radians and result needs to be in range [0,360)
    
    L = [(i + (1.916 * math.sin(math.radians(i))) + (0.020 * math.sin(math.radians(2 * i))) + 282.634) % 360 for i in M]
    
    # 5a calculate the Sun's right ascension
    
    RA = [(math.degrees(math.atan(0.91764 * math.tan(math.radians(i))))) for i in L]
    
    # 5b right ascension value needs to be in the same quadrant as L
    Lquadrant = [(math.floor(i/90)) * 90 for i in L]
    RAquadrant = [(math.floor(i/90)) * 90 for i in RA]
    
    # 5c right ascension value needs to be converted into hours
    RA = [(RA[i] + (Lquadrant[i] - RAquadrant[i]) ) / 15 for i in range(2)]
    
    
    # 6 calculate the Sun's declination
    sinDec = [0.39782 * math.sin(math.radians(i)) for i in L]
    cosDec = [math.cos(math.radians(math.degrees(math.asin(i)))) for i in sinDec]    

    #print("sinDec:", sinDec)
    #print("cosDec:", cosDec)

    # 7a calculate the Sun's local hour angle
    # cosH = (cos(zenith) - (sinDec * sin(latitude))) / (cosDec * cos(latitude))
    # cosH = [[rise:official,rise:civil, etc], [set:official,set:civil, etc]]
    
    cosH = [0] * 2
    
    for i in range(2):
        cosH[i] = [(j - (sinDec[i] * math.sin(math.radians(latitude)))) / (cosDec[i] * math.cos(math.radians(latitude))) for j in zenith]
    
    #7b finish calculating H and convert into hours
    
    # prep H for size
    H = [0] * 2 # rise and set
    H = [[0] * len(zenith) for i in H] # each rise and set has n elements based on size of zenith
    
    for i in range(len(zenith)):
        # rising times
        if abs(cosH[0][i]) > 1:
            H[0][i] = False
        else:
            H[0][i] = (360 - math.degrees(math.acos(cosH[0][i]))) / 15
            
        # setting times    
        if abs(cosH[1][i]) > 1:
            H[1][i] = False
        else:
            H[1][i] = math.degrees(math.acos(cosH[1][i])) / 15
        
    # 8 Calculate local mean time of rising / setting
    #T = H + RA - (0.06571 * t) - 6.622
    # 9 adjust back to UTC and correct adjust to range [0,24)
    # 10 add localtime offset
    # 11 ensure those False in H (i.e no rise or set) are reflected in the times
    T = [0] * 2
    
    for i in range(2):
        #print(H[i])
        T[i] = [ (((j + RA[i] - (0.06571 * t[i]) - 6.622 ) - lngHour) % 24 ) + offset if j is not False else False for j in H[i]]
    
    
    # T now contains all the rise and set times of the sun but in decimal hours i.e. 7.5 = 07:30; 7:25 = 07:15 etc or False where rise / set doesn't happen
    # Produce output dictionary with tuples of (rise,set) i.e. 'civil'(rise,set)
    
    OUT = dict(zip(zenith_labels,list(zip(T[0],T[1]))))
    
    return(OUT)