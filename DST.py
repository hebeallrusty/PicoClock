import utime

# return the offset required on UTC for GMT or BST.

# Rule - clocks change forward 1 hour at 1am last Sunday in March (UTC +1) and 1 hour back 2am last Sunday in October (UTC +0)

def DST_offset(tm):
    
    
    # get the last day of March - return is in seconds
    s = utime.mktime((tm[0],3,31,0,0,0,0,0))
    # convert it back to a tuple
    u = utime.localtime(s)
    # find what day of the week the last day is. 0 = Mon; 6 = Sun; therefore if we deduct the day number from the last day, we'll end up on a Monday, then take off one more to get to the last Sunday in the month
    d = u[6] # day of the week
    # BST starts as follows at 1am UTC: (in seconds)
    if d == 6: # if it's a sunday already then we don't need to adjust
        BST = utime.mktime((tm[0],3,31,1,0,0,0,0))
    else:
        BST = utime.mktime((tm[0],3,31 - d -1,1,0,0,0,0))
    
    # same logic as above but for October - return in seconds
    s = utime.mktime((tm[0],10,31,0,0,0,0,0))
    u = utime.localtime(s)
    d = u[6] # day of the week
    # GMT starts as follows at 2am UTC: (in seconds)
    if d == 6: # if it's a sunday already then we don't need to adjust
        GMT = utime.mktime((tm[0],10,31,2,0,0,0,0)) 
    else:
        GMT = utime.mktime((tm[0],10,31 - d -1,2,0,0,0,0))    
    
    # since everything is in seconds...
    UTC = utime.mktime(tm)
    
    if (UTC >= BST) and (UTC <= GMT):
        return(1)
    else:
        return(0)


#a = utime.mktime((2023,3,27,0,0,0,0,0))
#b = utime.localtime(a)
 
#print(DST_offset(b))