from machine import Pin, I2C
from ht16k33matrixfeatherwing import HT16K33MatrixFeatherWing
#from ht16k33 import HT16K33


ht16k33_i2c = I2C(1,scl=Pin(3), sda=Pin(2))

matrix = HT16K33MatrixFeatherWing(ht16k33_i2c)
#HT16K33.set_brightness(brightness=1)
matrix.set_brightness(15)

def glyph(g):
    # return an tuple with the digits to set as on for the glyph it represents. Not to be called directly, but through a function. It won't explode, but it'll only default producing glyphs that'll work on the first cluster on a cathode, which can hold 2nr'
    # returns [glyph segments, antiglyph segments for blanking]
    #
    # glyphs are 0 for the top seg going clockwise with 7 as the decimal point
    
    if g == 1: # 1
        return [(1,2),(0,3,4,5,6,7)]
    elif g == 2: # 2
        return [(0,1,6,4,3),(2,5,7)]
    elif g == 3: # 3
        return [(0,1,6,2,3),(4,5,7)]
    elif g == 4: # 4
        return [(5,6,1,2),(0,4,3,7)]
    elif g == 5: # 5
        return [(0,5,6,2,3),(1,4,7)]
    elif g == 6: # 6
        return [(0,5,4,3,2,6),(1,7)]
    elif g == 7: # 7
        return [(0,1,2),(5,6,4,3,7)]
    elif g == 8: # 8
        return [(0,1,2,3,4,5,6),(7,)]
    elif g == 9: # 9
        return [(0,5,6,1,2,3),(4,7)]
    elif g == 0: # 0
        return [(0,1,2,3,4,5),(6,7)]
    elif g == 11: # .
        return [(7,),(1,2,3,4,5,6)]
    elif g == 12: # [blank / space]
        return [(),(0,1,2,3,4,5,6,7)]
    elif g == 13: # b
        return [(5,4,3,2,6),(0,1,7)]
    elif g == 14: # t
        return [(5,4,3,6),(0,1,2,7)]
    elif g == 15: # I
        return [(4,5),(0,1,2,3,6,7)]
    elif g == 16: # n
        return [(2,4,6),(0,1,3,5,7)]
    elif g == 17: # s
        return [(0,5,6,2,3),(1,4,7)]
    elif g == 18: # d
        return [(1,2,3,4,6),(0,5,7)]
    elif g == 19: # c
        return [(0,3,4,5),(1,2,6,7)]
    elif g == 20: # e
        return [(0,5,6,1,4,3),(2,7)]
    elif g == 21: # r
        return [(4,6),(0,1,2,3,5,7)]
    elif g == 22: # o
        return [(6,2,3,4),(0,1,5,7)]
    elif g == 23: # A
        return [(0,1,2,4,5,6),(3,7)]
    else: # return an E
        return [(0,5,6,4,3),(1,2,7)]
    
    
def disp(d, bank):
    # plot a digit and display it on the bank noted
    
    # get the glyphs and anti-glyphs for digit g
    g,a = glyph(d)

    #print(g,a)
    # glyphs to light
    for i in g:
        #print("on:",i)
        matrix.plot(bank,i)
        
    # glyphs to blank off
    for i in a:
        #print("off:",i)
        matrix.plot(bank,i,ink=0)
        

def update_disp():
    matrix.draw()
        

# NOTE: matrix.plot(i,j) where i = 0-7 actual segments for banks 0-3 and i = 8 - 15 for banks 4 - 7; j is the cathode so the bank select

#for i in range(0,16):
#    for j in range(0,8):
#        matrix.plot(i,j)
#        matrix.draw()
#        utime.sleep(0.1)
#disp(2,15)
#disp(3,14)


#matrix.plot(