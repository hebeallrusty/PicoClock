import SECRETS # custom script with wifi names and passwords
import network
from time import sleep # only need sleep here

# connect to network

def WifiConnect():
    # create network object
    wlan = network.WLAN(network.STA_IF)
    # activate network card
    wlan.active(True)

    for i in SECRETS.WIFI:
        #print(i[0])
        wlan.connect(i[0],i[1])
        print("Attempting to connect to",i[0])
    
        # counter to allow connection attempt to give up if its taking too long
        j = 0
    
        while wlan.isconnected() == False:
            # go into a loop whilst it isn't connected and give an update to term
            print(j,": connecting to ", i[0])
        
            # sleep for 1 second
            sleep(1)
        
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
