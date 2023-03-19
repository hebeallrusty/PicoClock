# import standard libs
from machine import Pin, I2C
import time
import _thread


# import added libs
import bme280
#from bme280_float import *
from ds3231 import DS3231


# import custom scripts
from Seg import disp, update_disp
import Ntp_time
import Wifi # custom script to connect to the wifi

# blank display as random display shown on boot
for i in range(0,16):
    disp(12,i)
    
# display "init"
disp(15,0)
disp(16,1)
disp(15,3)
disp(14,4)
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

i2c0 = I2C(0,scl=Pin(5), sda=Pin(4))


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

# reset oscillator
ds._OSF_reset()

# set alarms on the ds3231 to trigger every second - to update display every second
ds.alarm1((0), match = ds.AL1_EVERY_S)
#while True:
#    print(ds.check_alarm(1))
#    time.sleep(0.5)

# set alarm on the ds3231 to trigger every minute so that time can be updated
#ds.alarm2((0), match = ds.AL2_EVERY_M)
#while True:
#    print(ds.check_alarm(2))
#    time.sleep(1)


# set up the rtc as the pico's clock; get the time from the ds3231 and then set var t as the local time for the loop
rtc = machine.RTC()
rtc.datetime(ds.datetime())
t = time.localtime()


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
#while True:
#    print(bme.read_temperature())
#    time.sleep(1)
#bme = BME280(i2c=i2c0, address=0x76)
#while True:
#    print(bme.values)
#    time.sleep(1)


##################
# display "booted"
disp(13,8)
disp(22,9)
disp(22,10)
disp(14,11)
disp(20,12)
disp(18,13)
update_disp()

updated_at = 0
print("entering main loop")
while True:
    
    while ds.check_alarm(1) == False:
        # don't do anything between clock ticks
        time.sleep (0.1)
    
    #update t as clock has ticked
    t = time.localtime()
    
    
    # check if time can be updated - every 20 mins
    if t[4] == 0 or t[4] == 20 or t[4] == 40:
        if t[4] == updated_at:
            print("already updated")
            pass
        else:
            # display "net   "
            disp(16,8)
            disp(20,9)
            disp(14,10)
            disp(12,11)
            disp(12,12)
            disp(12,13)
            update_disp()
            
            if Ntp_time.update_from_ntp() == True:
                # update was received from internet, update the ds3231
                ds.datetime((t[0],t[1],t[2],t[3],t[4],t[5],t[6]))
                updated_at = t[4]
            else:
                print("no update from internet")

    
    # to display it, they need to be in a zero-padded list so that the digits can be iterated over
    bme_t = [int(x) for x in f"{int(round(bme.temperature(),0)):02d}"]
    bme_h = [int(x) for x in f"{int(round(bme.humidity(),0)):02d}"]
    
   
    #print(t)
    
    hr = [int(x) for x in f"{t[3]:02d}"]
    mn = [int(x) for x in f"{t[4]:02d}"]
    sc = [int(x) for x in f"{t[5]:02d}"]
    
    yr = [int(x) for x in f"{t[0]:02d}"]
    mt = [int(x) for x in f"{t[1]:02d}"]
    dy = [int(x) for x in f"{t[2]:02d}"]
    
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
    
    # updated the display once
    update_disp()
    
    #time.sleep(0.1)

#disp(2,1)



