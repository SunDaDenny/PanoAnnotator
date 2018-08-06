import time

timeSave = 0

def getFPS():

    global timeSave
    durning = time.clock() - timeSave
    if not durning == 0:
        fps = 1.0 / (time.clock() - timeSave)
    else:
        fps = 0.0
    timeSave = time.clock()
    return fps