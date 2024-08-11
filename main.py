# import standard libs
from machine import Pin, I2C, UART
import time
import _thread
import math
import gc
import json
#import network
#import ntptime

# import added libs
import bme280
#from bme280_float import *
from ds3231 import DS3231


# import custom scripts
from Seg import disp, update_disp
#import Ntp_time
#import Wifi # custom script to connect to the wifi
from DST import DST_offset
from Sun import SunTimes
import TimeCalc

# default location - open from last saved location
with open('LastLocation.json','r') as f:
    print("Getting last location")
    location = json.load(f)
    
Lat = float(location['Latitude'])
Lon = float(location['Longitude'])
Ele = float(location['Elevation'])

print("Elevation:",Ele)

#Lat = 53.88
#Lon = -3.76

# blank display as random display shown on boot
for i in range(0,16):
    disp(12,i)
    
# display "init."
disp(15,8)
disp(16,9)
disp(15,10)
disp(14,11)
update_disp()


# display "i2c"
disp(15,0)
disp(2,1)
disp(19,2)
disp(0,3)
disp(12,4)
disp(12,5)

update_disp()

# bring in the i2c0 line

i2c0 = I2C(0,scl=Pin(5, pull=Pin.PULL_UP), sda=Pin(4,pull=Pin.PULL_UP))

# display "rtc"
disp(21,0)
disp(14,1)
disp(19,2)
disp(12,3)
disp(12,4)
disp(12,5)

update_disp()

# get time from internal ds3231
ds = DS3231(i2c0, addr=0x68)
#print(ds.datetime())
#ds._OSF_reset()
# check if time accurate
if ds.OSF() == 1:
    # display "batt  "
    disp(13,0)
    disp(23,1)
    disp(14,2)
    disp(14,3)
    disp(12,4)
    disp(12,5)
    update_disp()
    time.sleep(2)
    
    # reset flag
    ds._OSF_reset()

# set alarms on the ds3231 to trigger every second - to update display every second. Takes seconds timesource from the DS3231, not the internal clock
#ds.alarm1((0), match = ds.AL1_EVERY_S) # ironically ticks irregular - maybe the clone/fake chip?

#print("pass")

# set up the rtc as the pico's clock; get the time from the ds3231 and then set var t as the local time for the loop
#ds.datetime((29,10,16,2,9,45,11)) # for debug
rtc = machine.RTC() # pico's clock
rtc.datetime(ds.datetime()) # set pico clock from the ds3231
t = time.localtime()

print("t:",t)
print("rtc:",ds.datetime())

# display "sensor"

disp(17,0)
disp(20,1)
disp(16,2)
disp(17,3)
disp(22,4)
disp(21,5)
update_disp()

# bring up the sensor
bme = bme280.BME280(i2c=i2c0, address=0x76)


##################
# display "booted"
disp(13,0)
disp(22,1)
disp(22,2)
disp(14,3)
disp(20,4)
disp(18,5)
update_disp()

updated_at = -1 # to trigger updating of the time
first_run = 1 # to trigger the first cycle through e.g. get sunrise / set times
c = 0 # counter for cycling through the displays
lock = False
print("Initial lock released")
print("entering main loop")

lock_check = 0


def TickTock_run():
    print("Core 1 running")
    global lock
    global t
    global TimeUpdated
    global GPSSignal
    global first_run
    global c
    global Lat
    global Lon
    global lock_check
    global Ele # gps elevation

    GPSSignal = False
    
    TimeUpdated = False
    
    # custom glyphs for status indicators
       
    LED_MONDAY = [(0,),(1,2,3,4,5,6)]
    LED_TUESDAY = [(1,),(0,2,3,4,5,6)]
    LED_WEDNESDAY = [(2,),(1,0,3,4,5,6)]
    LED_THURSDAY = [(3,),(1,2,0,4,5,6)]
    LED_FRIDAY = [(4,),(1,2,3,0,5,6)]
    LED_SATURDAY = [(5,),(1,2,3,4,0,6)]
    LED_SUNDAY = [(6,),(1,2,3,4,5,0)]
    
    LED_WEEKDAY=[LED_MONDAY,LED_TUESDAY,LED_WEDNESDAY,LED_THURSDAY,LED_FRIDAY,LED_SATURDAY,LED_SUNDAY] # same order as utime's day of week
    
    LED_DATE = [(0,),(1,2,3,4,5,7)] # no 6 as this is used by LED_TIME_OFFSET for BST and GMT
    LED_TEMPERATURE = [(1,),(0,2,3,4,5,7)]
    LED_HUMIDITY = [(2,),(1,0,3,4,5,7)]
    LED_PRESSURE = [(3,),(1,2,0,4,5,7)]
    LED_SUNRISE = [(4,),(1,2,3,0,5,7)]
    LED_SUNSET = [(5,),(1,2,3,4,0,7)]
    LED_BST = [(6,),(7,)]
    LED_GMT = [(),(6,7)]
    
    LED_TIME_OFFSET = [LED_GMT,LED_BST] # offset is either a zero or a 1. Little bit hacky but BST is +1hr, other timezones would need to check anything other that 0 is returned as 1
    
    LED_DEBUG_ON = [(7,),()]
    LED_DEBUG_OFF = [(),(7,)]
    
    # custom Postitions
    LED_POS_DOW = 12
    LED_POS_STATUS_CYCLE = 13
    
    # these are the start positions - hours are at position 0 and 1
    LED_POS_HH = 0
    LED_POS_MM = 2
    LED_POS_SS = 4
    LED_POS_ONE = 8
    LED_POS_TWO = 10
    
    #core0 = _thread.start_new_thread(update_from_gps,())
    
    # positions of t list
    DAY = 2
    MONTH = 1
    YEAR = 0
    HOUR = 3
    MINUTE = 4
    SECOND = 5
    WEEKDAY = 6
    YEARDAY = 7
    

    #d = True
    
    while True: # main loop
        
        t_tick = time.ticks_us()
        
        while time.localtime()[SECOND] == t[SECOND]:
            time.sleep(0.01)
            # don't do anything between clock ticks

        #print("Tick:", time.ticks_diff(time.ticks_us(),t_tick) * 0.000001)
        
        # debug - how long does the code take to execute?
        t_start = time.ticks_us()
        
        gc.collect() # to stop the crashing with the second core
        #print(f"Memory: {gc.mem_alloc()} of {gc.mem_free()} bytes used.")
        
        #if d == True:
        #    disp(99,LED_POS_DOW,LED_DEBUG_ON)
        #else:
        #    disp(99,LED_POS_DOW,LED_DEBUG_OFF)
        #update_disp()
        
        #d = not(d)
        
        #update t as clock has ticked but sync first to ds3231 every half minute
        if t[SECOND] == 30:
            rtc.datetime(ds.datetime()) # update from DS3231
            
        t = time.localtime()
        #print("c1 rtc:",ds.datetime())
        #print("t:",t)
        #print("rtc:",ds.datetime())
        
        # Sync every 20 mins or first run get sunrise / set times periodically, update time and get current location
        if ((t[MINUTE] == 0) and (t[SECOND] == 0)) or ((t[MINUTE] == 20) and (t[SECOND] == 0)) or ((t[MINUTE] == 40) and (t[SECOND] == 0)) or (first_run == 1):
            print("updating sun times")
            first_run = 0
            gc.collect()
            # Get time from GPS here as second thread
            if lock == True:
                print("not updating GPS - lock active")
                lock_check +=1
                
                if lock_check == 5:
                    # lock is stuck - reboot clock
                    print("Lock is stuck, rebooting in 10 secs")
                    time.sleep(10)
                    machine.reset()
                
                
                pass
            else:
                lock_check = 0 # reset lock counter otherwise clock will reboot
                _thread.start_new_thread(update_from_gps,())
                print("running GPS Code")
            
            # Get Location from GPS
            print("SUN TIMES BASED ON LOCATION:",Lat, Lon)
            sun = SunTimes(t[YEAR],t[MONTH],t[DAY],Lat, Lon, DST_offset(t))
            #print(s)
            sunrise = TimeCalc.Hrs(sun['Official'][0])
            sunset = TimeCalc.Hrs(sun['Official'][1])
            #solar_day = TimeCalc.Hrs(sun['Official'][1] - sun['Official'][0])
            # convert decimal time to hrs and mins
           

        
        # to display it, they need to be in a zero-padded list so that the digits can be iterated over
        bme_temperature = bme.temperature()
        bme_humidity = bme.humidity()
        bme_pressure = bme.pressure()
        
        # correct pressure for sea level using formula: from https://keisan.casio.com/exec/system/1224575267
        #	P_sl = P (1- (0.0065h/(T + 0.0065h + 273.15)^-5.257
        
        bme_pressure_sl = bme_pressure * (1 - ((0.0065 * Ele) / (bme_temperature + (0.065 * Ele) + 273.15)) )**(-5.257)
        #print("sea level pressure:",bme_pressure_sl)
        #print("bme pressure:",bme_pressure)
        
        bme_t = [int(x) for x in f"{int(math.trunc(bme_temperature)):02d}"] # get first two digits
        bme_t_dec = [int(x) for x in f"{int(math.trunc((bme_temperature - math.trunc(bme_temperature))*100)):02d}"] # get first two decimal places
        
        bme_h = [int(x) for x in f"{int(math.trunc(bme_humidity)):02d}"] # get first two digits
        bme_h_dec = [int(x) for x in f"{int(math.trunc((bme_humidity - math.trunc(bme_humidity))*100)):02d}"] # get first two decimal places
        
        bme_p = [int(x) for x in f"{int(math.trunc(bme_pressure_sl)):04d}"]
       
        #print(t)
        
        # Time is reported as UTC, however we need to add an offset if it is BST or GMT
        # Convert time to seconds, add the offset and convert back to the tuple of time
        tl_sec = time.mktime(t) + (3600 * DST_offset(t))
        tl = time.localtime(tl_sec)
        
        hr = [int(x) for x in f"{tl[3]:02d}"]
        mn = [int(x) for x in f"{tl[4]:02d}"]
        sc = [int(x) for x in f"{tl[5]:02d}"]
        
        yr = [int(x) for x in f"{tl[0]:02d}"]
        mt = [int(x) for x in f"{tl[1]:02d}"]
        dy = [int(x) for x in f"{tl[2]:02d}"]
        
        sunrise_hr = [int(x) for x in f"{sunrise[0]:02d}"]
        sunrise_mn = [int(x) for x in f"{sunrise[1]:02d}"]
        #print("sun:",sunrise_hr)

        sunset_hr =  [int(x) for x in f"{sunset[0]:02d}"]
        sunset_mn =  [int(x) for x in f"{sunset[1]:02d}"]
       
        #print(yr)
        
        # top display is [0-5]; bottom display is [8-11]; status ligts are [12-13]

        # display BST / GMT
        disp(99,LED_POS_STATUS_CYCLE,LED_TIME_OFFSET[DST_offset(t)])
        
        # display Day of Week
        disp(99,LED_POS_DOW,LED_WEEKDAY[t[6]])

        
        # display cycle - each 7 seg is 2 bit
        for i in range(0,2): # update 1st bit's first then second
            #print(bme_t_list[i])

            # update time
            disp(hr[i],LED_POS_HH + i)
            disp(mn[i],LED_POS_MM + i)
            disp(sc[i],LED_POS_SS + i)
            
            # multi display cycle
            #print(c)
            if c % 24 == 0:
                # display date
                disp(99,LED_POS_STATUS_CYCLE,LED_DATE)
                
                disp(dy[i],LED_POS_ONE+i)
                disp(mt[i],LED_POS_TWO+i)
                disp(27,LED_POS_ONE + 1) # add dot
                
                
            elif c % 24 == 4:
                # display Temperature
                
                disp(99,LED_POS_STATUS_CYCLE,LED_TEMPERATURE)
                
                disp(bme_t[i],LED_POS_ONE+i)
                disp(bme_t_dec[i],LED_POS_TWO+i)
                disp(27,LED_POS_ONE + 1) # add dot
                
            elif c % 24 == 8:
                # display Humidity
                
                disp(99,LED_POS_STATUS_CYCLE,LED_HUMIDITY)
                
                disp(bme_h[i],LED_POS_ONE+i)
                disp(bme_h_dec[i],LED_POS_TWO+i)
                disp(27,LED_POS_ONE + 1) # add dot
                
            elif c % 24 == 12:
                # display Pressure
                disp(99,LED_POS_STATUS_CYCLE,LED_PRESSURE)
                
                disp(bme_p[i],LED_POS_ONE+i)
                disp(bme_p[i+2],LED_POS_TWO+i)
                disp(28,LED_POS_ONE + 1) # remove dot
                
            elif c % 24 == 16:
                disp(99,LED_POS_STATUS_CYCLE,LED_SUNRISE)
                
                disp(sunrise_hr[i],LED_POS_ONE + i)
                disp(sunrise_mn[i],LED_POS_TWO + i)
                disp(27,LED_POS_ONE + 1)
            
            elif c % 24 == 20:
                disp(99,LED_POS_STATUS_CYCLE,LED_SUNSET)
                
                disp(sunset_hr[i],LED_POS_ONE + i)
                disp(sunset_mn[i],LED_POS_TWO + i)
                disp(27,LED_POS_ONE + 1)               
            
                
        # reset counter for multi display        
        c += 1
        c %= 24

            
        # blink the dots every other second
        if (tl[SECOND] % 2) == 1:
            disp(27,1)
            disp(27,3)
            disp(27,5)
        

        
        # updated the display once
        update_disp()
        #print(sc)
        #print("Exec:", time.ticks_diff(time.ticks_us(),t_tick) * 0.000001)
        
        #time.sleep(0.1)
        #print("core 1 done")

def update_from_gps():
    # to be run from second thread
    
    global lock
    lock = True # lock this code so that it can only execute from main thread once at a time
    print("Lock active")
    import utime as utime
    
    
    global t
    global updated_at
    global TimeUpdated
    global GPSSignal
    global Lat
    global Lon
    global Ele
    
    # locations within GNRMC statment of data of interest
    GPS_TIME = 1
    GPS_LAT = 3
    GPS_LAT_DIR = 4
    GPS_LON = 5
    GPS_LON_DIR = 6
    GPS_DATE = 9
    
    # elevation within GNGGA stamente of data of interest
    GPS_ELEVATION = 9
    GPS_SATELLITES = 7
    

    #import utime as utime
    #print("Waiting 10 secs")
    #utime.sleep(10)
    #print("done waiting - bring up the uart")
    
    # bring up UART
    #uart = UART(0, baudrate = 115200, tx=Pin(0), rx=Pin(1), bits=8, parity=None, stop=1, timeout = 10, timeout_char = 10)
    
    # pps will let us know that the GPS signal is being received
    pps = Pin(22,Pin.IN, Pin.PULL_DOWN)
    #pps = 0
    print("running GPS")
    
    # set up a buffer to get the uart characters one at a time
    #buf = b""
    #buffer_ready = False
    
    n = 0 # counter to allow code to time-out
    
    # check for a pps signal - if there is a pulse - then the module is recieving a signal.
    
    # PPS indicates when the proceeding (i.e next) NMEA sentence was valid
    # i.e BEEP, the time at the beep WAS 12:53.
    
   
    while pps.value() == False: # pps will only fire once per second so this could return false when there is a signal - time-out after 1000 attempts
        n += 1
        #print(n)
        utime.sleep(0.01)
        if n == 6000: # about 60 ish seconds
            print("pps timed out")
            lock = False
            print("lock released")
            TimeUpdated = False
            return
    
    # mark when we received a pps signal
    t_PPS_signal = utime.ticks_us()
    ds._OSF_reset()
    
    #utime.sleep(1)
    # search for the $GNRMC statement from the GPS - this contains the time and location.
    #print("pps active")
    #return
    
    n = 0 # reset counter
    
    # keep searching for the right statment from the GPS module

    
    while n < 10: # time out after this number of GPS statments. Anything after the loop means we failed to get a time
        
        #print("PPS Received")
        # if we are here - we have received a GPS signal - now read the NMEA sentences

        # mark time of the start of an NMEA sentence
        t_start_NMEA = utime.ticks_us()
        
        GNRMC = Get_NMEA_Statement("$GNRMC",20)
        
        t_end_NMEA = utime.ticks_us() # mark time at end of NMEA sentence
        
        if GNRMC == False:
            print("Failed to receive GNRMC statment")
            n +=1
            pass
        elif Validate_GNRMC(GNRMC,GPS_DATE,GPS_TIME,GPS_LON,GPS_LAT) == False:
            print("Validation of GNRMC failed")
            n += 1
            pass
        else:
            print("GNRMC data is complete")
            GPSSignal = True # receiveing a time signal
            # update ds3231
            # gps time - display on repl
            
            GNRMC = GNRMC.split(',')
                
            GPS_HH = GNRMC[GPS_TIME][0:2]
            GPS_MM = GNRMC[GPS_TIME][2:4]
            GPS_SS = GNRMC[GPS_TIME][4:6]
            
            GPS_DAY = GNRMC[GPS_DATE][0:2]
            GPS_MONTH = GNRMC[GPS_DATE][2:4]
            GPS_YEAR = GNRMC[GPS_DATE][4:6]
            
            #test if received data is "valid"

            if Validate_GPS_Time(GPS_HH,GPS_MM,GPS_SS,GPS_DAY,GPS_MONTH,GPS_YEAR)[0] == False:
                # release the lock
                lock = False
                print("lock released")
                return
            
            # we know when the original pps fired; we know when we started a valid NMEA sentence. Given each pps fires on a whole second, and the start of the NMEA statement
            # is after the pps by some margin of error (epsilon), we approx know when the pps fired for the valid time.
            # now a new pps has fired, we should know the offset (x) to add to the time to sync to the gps time.
            # 
            # epsilon is the difference between the original pps and when we started a valid sentence modulo 1e-5 (i.e microseconds)
            
            utime.sleep(2) # seems to work better with a small snooze
            
            epsilon = (utime.ticks_diff(t_start_NMEA,t_PPS_signal) * 0.000001) % 1
            
            print("epsilon",epsilon)
            
                
            # get next pps
            while pps.value() == False:
                utime.sleep(0.01)
                #print("sleeping to sync to pps to time")
            
            # x is the offset to apply in whole seconds
            x = (utime.ticks_diff(utime.ticks_us(),t_start_NMEA) * 0.000001) - epsilon
            print("offset seconds",x)
            x = math.floor(x)
            #x = round(x,0)

            
            timestr = ((int(GPS_YEAR),int(GPS_MONTH),int(GPS_DAY),int(GPS_HH),int(GPS_MM),int(GPS_SS)+x))

            # update ds3231
            ds.datetime(timestr) # add adjustment as new pps signal denotes new second
            
            # update pico with the ds3231
            rtc.datetime(ds.datetime())
            print("time:", GPS_HH, GPS_MM, GPS_SS)
            print("date:",GPS_DAY , GPS_MONTH, GPS_YEAR)
            #t = 
            print("TIME UPDATED")
            TimeUpdated = True
            updated_at = GPS_MM
            
            # update Lon and Lat ; W and S are negative
            # convert to degrees from dddmm.mmmm
            
            # validate location
            
            if Validate_GPS_Location(GNRMC[GPS_LON],GNRMC[GPS_LAT])[0] == False:
                # release the lock
                lock = False
                print("lock released")
                return                            
            
            lon = int(GNRMC[GPS_LON][0:3]) + float(GNRMC[GPS_LON][3:7])/60
            lat = int(GNRMC[GPS_LAT][0:2]) + float(GNRMC[GPS_LAT][2:6])/60
            
            if GNRMC[GPS_LON_DIR] == "W":
                lon *= -1
                print("adjusted Lon to negative")
            if GNRMC[GPS_LAT_DIR] == "S":
                lat *= -1
                print("adjusted Lat to negative")
            
            # save location if necessary then update the global location variables
            #SaveLocation(lon,lat,Ele)
            
            #Lon = lon
            #Lat = lat
            
            print("Location: ",lat,lon)
            
            # release the lock
            #lock = False
            #print("lock released")
            
            #break
            #return
            
            
            
            print("checking elevation")
            
            GNGGA = Get_NMEA_Statement("$GNGGA",20)
            #print(GNGGA)
            
            if GNGGA == False:
                # release the lock and return - don't need to wait for a valid elevation
                lock = False
                return
            elif Validate_GNGGA(GNGGA,GPS_ELEVATION,GPS_SATELLITES) == False:
                lock = False
                return
            
            # if we are here - then GNGGA is valid
            GNGGA = GNGGA.split(',')
            
            # elevation will only be fairly accurate if there lots of
            print("satellites:",int(GNGGA[GPS_SATELLITES]))
            if int(GNGGA[GPS_SATELLITES]) < 10:
                print("Not enough satellites in view for Elevation")
                Elevation = Ele # take elevation to be what it currently is so we don't store something inaccurate (and wear out the flash)
            else:
                Elevation = float(GNGGA[GPS_ELEVATION])


            print("Saving Longitude, Latitude and Elevation to file")
            # save everything to file
            SaveLocation(Lon,Lat,Elevation)

        
            # update system
            Ele = Elevation
            Lon = Lon
            Lat = Lat
            
            print("releasing the lock")
            lock = False #release lock
            return
                
                
  
    print("Failed to get valid update from GPS")  
    lock = False  # if we are outside the loop - release the lock
    print("lock released")
    TimeUpdated = False
    return


def Validate_GPS_Time(Hour,Minute,Second,Day,Month,Year):
    
    # Rules:
    #	r1. Values should be numeric
    #	r2. Hours less than 24
    #	r3. Minutes less than 60
    #	r4. Seconds less than 60
    #	r5. Month less than 12
    #	r6. Days appropriate to month
    #	r7. Years - ???
    
    valid_days = (31,28,31,30,31,30,31,31,30,31,30,31)
    
    # r1
    try:
        HOUR = int(Hour)
        MINUTE = int(Minute)
        SECOND = int(Second)
        DAY = int(Day)
        MONTH = int(Month)
        YEAR = 2000+int(Year)
    
    except Exception as error:
        print("r1 failed in Validate_GPS_Time:", error)
        
        return(False, "Failed r1 - numeric check")
    
    # r2
    
    if (HOUR >= 24) or (HOUR < 0):
        return(False, "Failed r2 - hour check")
    
    # r3
    
    if (MINUTE >= 60) or (MINUTE < 0):
        return(False, "Failed r3 - minute check")
    
    # r4
    
    if (SECOND >= 60) or (SECOND < 0):
        return(False, "Failed r4 - second check")
    
    # r5
    
    if (MONTH > 12) or (MONTH < 0):
        return(False, "Failed r5 - month check")
    
    #r7
    
    if YEAR < 0:
        return(False,"Failed r7 - year check")
    
    # r6
    valid_days = (31,28,31,30,31,30,31,31,30,31,30,31)
    
    if DAY > 0:
        
        # day adjustment for leap year
        dy_adj = 0
        
        # allow for February - add a day for a leap year; otherwise no adjustment
        if MONTH == 2:
            dy_adj = ( YEAR % 4 == 0 and (YEAR % 100 != 0 or YEAR % 400 == 0))
        
        #print(MONTH)
        #print(dy_adj)
        #print(valid_days[MONTH - 1] + dy_adj)
            
        if DAY > valid_days[MONTH - 1] + dy_adj:
            return(False, "Failed r6 - day check")
    else:
        return(False, "Failed r6 - day check")
            
        
    
    return(True,"Passed Validation of Time")
    

def Validate_GPS_Location(Longitude,Latitude):
    #print("Long:",Longitude,"Lat:",Latitude)
    
    # rules:
    #	r1 - must be numeric
    #	r2 - must be sane

    #r1

    try:
        Major_Lon = int(Longitude[0:3])
        Major_Lat = int(Latitude[0:2])

        Minor_Lon = float(Longitude[3:7])/60
        Minor_Lat = float(Latitude[2:6])/60

    except Exception as error:
        print("r1 failed in Validate_GPS_Location:", error)
        return(False, "Failed r1 - numeric check")

    #print(Major_Lon)
    #print(Major_Lat)

    #r2
    if abs(Major_Lon) > 180:
        return(False,"Failed r2 - absolue value of Longitude greater than 180 deg")
        
    if abs(Major_Lat) > 90:
        return(False,"Failed r2 - absolute value of Latitude greater than 90 deg")
    
    return(True, "Passed validation of location")
    

def SaveLocation(Longitude,Latitude,Elevation):
    # assumes validation of co-ordinates already
    
    # the coordinates already in memory
    global Lat
    global Lon
    global Ele
    
    if (abs(Longitude - Lon) < 0.05) and (abs(Latitude - Lat) < 0.05) and (abs(Elevation - Ele) < 10):
        print("not saving location to file since we are close enough")
        return # farily close - no need to write to file
    else:
        # write coodinates to file
        print("saving location for future use")
        location = {"Longitude":Longitude,"Latitude":Latitude,"Elevation":Elevation}
        with open('LastLocation.json','w') as f:
            json.dump(location,f)
            
    
    return

def Get_NMEA_Statement(statement,timeout):
    print("Getting NMEA Statement",statement)
    n = 0 # counter

    # bring up UART
    uart = UART(0, baudrate = 115200, tx=Pin(0), rx=Pin(1), bits=8, parity=None, stop=1, timeout = 10, timeout_char = 10)
        
    # set up a buffer to get the uart characters one at a time
    buf = b""
    buffer_ready = False

    while n < timeout:

        
        if uart.any():
            # mark time of the start of an NMEA sentence
            #t_start_NMEA = utime.ticks_us()
            # read buffer character one at a time: from jcf on micropython forums
            c = uart.read(1)
            if c == b'\n':
                buffer_ready = True
            else:
                buf += c
            if buffer_ready:
                #print("BUFFER:", buf) # !!!enabling print statements here delays the buffer and can cause incorrect nmea statements!!!
                #print(n)
                #t_end_NMEA = utime.ticks_us() # mark time at end of NMEA sentence
                n += 1 
              
                
                
                # convert the buffer to a string, and chop off the begining and end to get the GPS statements
                #print(str(buf)[2:8])
                if str(buf)[2:8] == statement:
                    return(str(buf)[2:-3])
                #print(data[0:6])
                
                # reset buffer
                buf = b""
                buffer_ready = False
    
    
    return(False)

def Validate_GNRMC(gnrmc,date_pos,gps_time_pos,gps_lon_pos,gps_lat_pos):
    
    gnrmc = gnrmc.split(',')
    
    if len(gnrmc) < 13:
        # not enough elements in output
        print("not enough items in GNRMC output")
        return(False)
            
    elif not all([gnrmc[date_pos], gnrmc[gps_time_pos], gnrmc[gps_lon_pos],gnrmc[gps_lat_pos]]):
        # we have blanks in the data received
        print("data is incomplete")
        return(False)
    
    # data is complete
    return(True)
    
def Validate_GNGGA(gngga,elev_pos,sat_pos):
    
    if len(gngga) < 13:
        # not enough elements in output
        print("not enough items in GNGGA output")
        return(False)
    
    elif not all([gngga[elev_pos],gngga[sat_pos]]):
        # we have blanks in the data received
        print("data is incomplete")
        
        return(False)
    else:
        print("checking if Elevation is valid")
        try:
            Elevation = float(gngga[elev_pos])
            Satellites = int(gngga[sat_pos])
        except Exception as error:
            print("Elevation or satellite count not Numeric:",error)
            lock = False
            return(False)
    
    return(True)


#_thread.start_new_thread(update_from_gps,())
# run the network items on core0 so that thread doesn't freeze on the wifi activation and utilisation
#update_from_ntp()

# display "gps"
disp(29,8)
disp(30,9)
disp(17,10)
disp(12,11)
update_disp()


#print(Get_NMEA_Statement("$GNGGA",200))
#update_from_gps()
TickTock_run()