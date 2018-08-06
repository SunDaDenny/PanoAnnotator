import sys
import math

import utils 
import configs.Params as pm

from .GeoPoint import *
from .Scene import *
from .Annotation import *

geInstanceCount = 0

class GeoEdge(object):

    def __init__(self, scene, gPoints):

        self.__scene = scene

        if(len(gPoints)<2):
            print("Two point at least")

        self.gPoints = gPoints
        self.vector = (0, 0, 0)
        
        self.sample = []
        self.coords = []
        
        self.id = 0

        self.init()
    
        global geInstanceCount
        geInstanceCount += 1
        self.id = geInstanceCount

    def init(self):
        
        p1 = self.gPoints[0].xyz
        p2 = self.gPoints[1].xyz
        self.vector = utils.pointsDirection(p1, p2)

        self.sample = utils.pointsSample(p1, p2, 15)
        self.coords = utils.points2coords(self.sample)


    def checkCross(self):
        for i in range(len(self.coords)-1):
            isCross, l, r = utils.pointsCrossPano(self.sample[i],
                                                 self.sample[i+1])
            if isCross:
                return True, l, r
        return False, None, None
        
    