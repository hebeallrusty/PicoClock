from machine import Pin, I2C, UART
import time
    
# bring up UART
uart = UART(0, baudrate = 115200, tx=Pin(0), rx=Pin(1), bits=8, parity=None, stop=1, timeout = 10, timeout_char = 10)
pps = Pin(22,Pin.IN, Pin.PULL_DOWN)    

while True:
    print(pps.value())
    time.sleep(0.01)
    #start = time.ticks_us()
    #while pps.value() == False:
    #    print(0)
    #    time.sleep(0.1)
    #print(1)    
    #print(time.ticks_diff(time.ticks_us(),start))