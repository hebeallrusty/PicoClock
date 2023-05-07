# import standard libs
from machine import Pin, I2C
import time
import _thread
import network
import ntptime

# import added libs
import bme280
#from bme280_float import *
from ds3231 import DS3231


# import custom scripts
from Seg import disp, update_disp
#import Ntp_time
import Wifi # custom script to connect to the wifi
from DST import DST_offset

# blank display as random display shown on boot
for i in range(0,16):
    disp(12,i)
    
# display "init."
disp(15,0)
disp(16,1)
disp(15,2)
disp(14,3)
disp(27,3)
update_disp()


# display "i2c  "
disp(15,8)
disp(2,9)
disp(19,10)
disp(0,11)
disp(12,12)
disp(12,13)
update_disp()

# bring in the i2c0 line

i2c0 = I2C(0,scl=Pin(5, pull=Pin.PULL_UP), sda=Pin(4,pull=Pin.PULL_UP))
#i2c0 = I2C(0,scl=Pin(5), sda=Pin(4))


# display "rtc   "
disp(21,8)
disp(14,9)
disp(19,10)
disp(12,11)
disp(12,12)
disp(12,13)
update_disp()

# get time from internal ds3231
ds = DS3231(i2c0, addr=0x68)
#print(ds.datetime())

# check if time accurate
if ds.OSF() == 1:
    # display "batt  "
    disp(13,8)
    disp(23,9)
    disp(14,10)
    disp(14,11)
    disp(12,12)
    disp(12,13)
    update_disp()
    time.sleep(2)
    
    # reset flag
    ds._OSF_reset()

# set alarms on the ds3231 to trigger every second - to update display every second
ds.alarm1((0), match = ds.AL1_EVERY_S)

print("pass")

# set up the rtc as the pico's clock; get the time from the ds3231 and then set var t as the local time for the loop
#ds.datetime((29,10,16,2,9,45,11)) # for debug
rtc = machine.RTC()
rtc.datetime(ds.datetime())
t = time.localtime()

print("t:",t)
print("rtc:",ds.datetime())

# display "sensor"

disp(17,8)
disp(20,9)
disp(16,10)
disp(17,11)
disp(22,12)
disp(21,13)
update_disp()

# bring up the sensor
bme = bme280.BME280(i2c=i2c0, address=0x76)

disp(16,8)
disp(20,9)
disp(14,10)
disp(12,11)
disp(12,12)
disp(12,13)
update_disp()

# activate wlan - wlan only works properly on Core0 not Core1 which freezes it
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

##################
# display "booted"
disp(13,8)
disp(22,9)
disp(22,10)
disp(14,11)
disp(20,12)
disp(18,13)
update_disp()

updated_at = -1
#lock = False
print("entering main loop")


def core1_run():
    print("Core 1 running")
    #global lock
    global t
    global WifiStatus
    global TimeUpdated
    #lock = True
    WifiStatus = []
    WifiStatus.append(False)
    
    TimeUpdated = False
    
    while True:
        
        while ds.check_alarm(1) == False:
            # don't do anything between clock ticks
            time.sleep (0.1)
        
        #update t as clock has ticked
        t = time.localtime()
        #print("c1 rtc:",ds.datetime())
        
        # to display it, they need to be in a zero-padded list so that the digits can be iterated over
        bme_t = [int(x) for x in f"{int(round(bme.temperature(),0)):02d}"]
        bme_h = [int(x) for x in f"{int(round(bme.humidity(),0)):02d}"]
        
       
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
        
        #print(yr)
        
        # display as follows
        # temperature digits in 14 and 15
        # humidity digits in 6 and 7
        
        # hour in 0-1
        # min in 2-3
        # sec in 4-5
        
        # day in 8-9
        # month in 10-11
        # year in 12-13
        

            
        for i in range(0,2):
            #print(bme_t_list[i])
            disp(bme_t[i],14+i)
            disp(bme_h[i],6+i)
            
            disp(hr[i],0+i)
            disp(mn[i],2+i)
            disp(sc[i],4+i)
            
            disp(dy[i],8+i)
            disp(mt[i],10+i)
            disp(yr[i+2],12+i)
            
        #print("WIFI STATUS",WifiStatus[0])
        
        
        # by default the below statuses will be wiped each second due to the segment code omitting the dot; only need to check if true each time
        # every 20 mins these status's should change when the Networking code runs
        # add status of wifi
        if WifiStatus[0] == True:
            disp(27,15)
        # add status of update
        if TimeUpdated == True:
            disp(27,7)
            
        # blink the dots every other second
        if (tl[5] % 2) == 1:
            disp(27,1)
            disp(27,3)
            disp(27,5)

        
        # updated the display once
        update_disp()
        
        #time.sleep(0.1)
        #print("core 1 done")


def update_from_ntp():
    #global lock
    global t
    global updated_at
    global WifiStatus
    global TimeUpdated
    #print("update_from_ntp triggered")
    
    # execute main thread on core 1 - wifi doesn't work correctly on core 0
    core1 = _thread.start_new_thread(core1_run,())
    #print("post thread")

    while True:
        
        #
        #print("Inside NTP Loop")
        #print(t)
        #time.sleep(1)
        #print("ntp rtc:",ds.datetime())
        # check if time can be updated - every 20 mins
        if t[4] == 0 or t[4] == 20 or t[4] == 40 or updated_at == -1:
            if t[4] == updated_at:
                # already updated
                pass
            else:
                # connect to internet first and get status
                WifiStatus = Wifi.WifiConnect(wlan)
                
                print(WifiStatus)
                
                if WifiStatus[0] == True:
                    
                    try:
                        print("updating time from internet")            
                        ntptime.settime()
                        # update the ds3231 rtc
                        t = time.localtime()
                        #print("from ntptime",t)
                        
                        # update the ds3231 module; rtc doesn't need updating as ntptime does that
                        ds.datetime((t[0],t[1],t[2],t[3],t[4],t[5],t[6]))
                        TimeUpdated = True
                        # record when the update occured so that we don't hammer the wifi or NTP server
                        updated_at = t[4]
                    except Exception as e:
                        TimeUpdated = False
                        
                        # might error out - get the error number and print 
                        print(e)
                        print("no update on time")
      
                else: # network down - display "d"
                    TimeUpdated = False
                    print("no wifi")
                    
            
        #print("Core 0 done")
        
        time.sleep(10)
        

# run the network items on core0 so that thread doesn't freeze on the wifi activation and utilisation
update_from_ntp()
