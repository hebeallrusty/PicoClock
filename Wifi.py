import SECRETS # custom script with wifi names and passwords
#import network
from utime import sleep # only need sleep here

# connect to network

# constants that wifi status will output to move onto the next connection if there is a problem
STAT_IDLE = 0 # no connection and no activity,
STAT_CONNECTING = 1 # connecting in progress,
STAT_WRONG_PASSWORD = -3 # failed due to incorrect password,
STAT_NO_AP_FOUND = -2 #  failed because no access point replied,
STAT_CONNECT_FAIL = -1 # failed due to other problems,
STAT_GOT_IP = 3 # connection successful.

def WifiConnect(wlan):
    print("Entering WifiConnect()")
    # create network object
    #wlan = network.WLAN(network.STA_IF)
    #print("defined wlan")
    # activate network card
    #wlan.active(True)
    #print("wlan card switched on")
    
    if wlan.isconnected() == True:
        print("already connected")
        # probably want to find the name for consistent output, but first value will return True anyway but network name won't be included
        return([wlan.isconnected()])
    else:
        for i in SECRETS.WIFI:
            #print(i[0],i[1])
            wlan.connect(i[0],i[1])
            print("Attempting to connect to",i[0])
    
            # counter to allow connection attempt to give up if its taking too long
            j = 0
    
            while wlan.isconnected() == False:
                # go into a loop whilst it isn't connected and give an update to term
                print(j,": connecting to ", i[0])
                
                
                # sleep for 1 second
                sleep(1)
                
                # check ongoing progress and break if there is a problem
                print("wlan status:", wlan.status())
                if wlan.status() == STAT_NO_AP_FOUND:
                    break
                elif wlan.status() == STAT_WRONG_PASSWORD:
                    break
                elif wlan.status() == STAT_CONNECT_FAIL:
                    break
        
                # increment counter
                j = j +1
        
                # break out if too many attempts
                if j > 10:
                    print("failed to connect to", i[0])
                    break
        
            if wlan.isconnected():
                print("connected to",i[0])
                return([wlan.isconnected(),i[0]])
    
    return([wlan.isconnected()])
#print(wlan.ifconfig())

def WifiDisconnect():
    print("disconnecting")
    network.WLAN(network.STA_IF).deinit
