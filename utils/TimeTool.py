import time

timeStart = 0
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

def resetTimer():
    global timeStart
    timeStart = 0

def getRunTime():
    global timeStart
    print(time.clock() - timeStart)
    timeStart = 0

