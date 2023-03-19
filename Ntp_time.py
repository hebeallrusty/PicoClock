import ntptime
import Wifi
import time

def update_from_ntp():
    
    # connect to internet first and get status
    WifiStatus = Wifi.WifiConnect()
    
    #print(WifiStatus)
    
    if WifiStatus[0] == True:
    #print("in wifistatus loop main")
    # let the outside world know that connected to internet - display "c" for connected
    #disp(19,15)
    #time.sleep(10)
        try:
            ntptime.settime()
            print("updating time from internet")
            # update the ds3231 rtc
            t = time.localtime()
            return(True)
            #print(t)
            #ds.datetime((t[0],t[1],t[2],t[3],t[4],t[5],t[6]))
        except:
            print("no update from internet")
            return(False)
            #rtc.datetime(ds.datetime())        
    else: # network down - display "d"
        # get the time from the DS3213
        #disp(18,15)
        print("no wifi")
        return(False)
        #rtc.datetime(ds.datetime())