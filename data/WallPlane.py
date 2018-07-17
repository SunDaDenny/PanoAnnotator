
import sys
import random
import math 

import utils 
from .Scene import *
from .GeoPoint import *

wpInstanceCount = 0

class WallPlane(object):

    def __init__(self, scene, geoPoints):

        self.__mainScene = scene

        if(len((geoPoints))<2):
            print("Two point at least")
            
        self.geoPoints = geoPoints
        self.color = (random.random(), random.random(), 
                      random.random())

        self.normal = (0, 0, 0)
        self.planeEquation = (0, 0, 0, 0) 

        self.mesh = []
        self.meshProj = []

        self.id = 0

        self.init()
    
    def init(self):

        #gps = self.geoPoints
        #gps.sort(key=lambda x:x.coords[0])

        self.calcMeshByPoints()

        global wpInstanceCount
        wpInstanceCount += 1
        self.id = wpInstanceCount

    def moveByNormal(self, val):

        vec = [self.normal[0]*val, self.normal[1]*val, self.normal[2]*val]
        
        for gp in self.geoPoints:
            gp.moveByVector(vec)

        self.calcMeshByPoints()

    def calcMeshByPoints(self):

        self.mesh = []
        self.meshProj = []
        
        gps = self.geoPoints
        cameraH = self.__mainScene.label.getCameraHeight()
        cam2ceilH = self.__mainScene.label.getCam2CeilHeight()

        self.mesh = [(gps[0].xyz[0], cam2ceilH, gps[0].xyz[2]),
                    (gps[1].xyz[0], cam2ceilH, gps[1].xyz[2]),
                    (gps[1].xyz[0], -cameraH, gps[1].xyz[2]),
                    (gps[0].xyz[0], -cameraH, gps[0].xyz[2])]

        vec1 = list(utils.calcPointsDirection(self.mesh[0], self.mesh[1]))
        vec2 = list(utils.calcPointsDirection(self.mesh[0], self.mesh[3]))
        
        self.normal = tuple(np.cross(vec1,vec2))
        
        pd = 0
        for i in range(3):
            pd -= self.normal[i] * self.mesh[0][i]
        self.planeEquation = self.normal + (pd,)

        self.meshProj = utils.mesh2pano(self.mesh)

    def checkRayHit(self, vec, orig=(0,0,0)):

        tmp = 0
        for i in range(3):
            tmp += self.planeEquation[i] * vec[i]

        if tmp < 0.00001:
            return False

        t = -self.planeEquation[3] / tmp
        point = (vec[0] * t, vec[1] * t, vec[2] * t)

        if self.mesh[2][1] <= point[1] <= self.mesh[0][1]:

            p1 = (point[0], self.mesh[0][1], point[2])
            dis1 = utils.calcPointsDistance(p1, self.mesh[0])
            dis2 = utils.calcPointsDistance(p1, self.mesh[1])
            dis3 = utils.calcPointsDistance(self.mesh[0], self.mesh[1])

            if dis1 + dis2 <= dis3 * 1.005:
                return True

        return False

    def getConnectPoint(self, other):

        center = None        
        for p1 in self.geoPoints:
            for p2 in other.geoPoints:
                if p1 == p2:
                    center = p1
        if not center:
            return None, None
        
        outers = []
        gps = self.geoPoints + other.geoPoints
        for point in gps:
            if not point == center:
                outers.append(point)

        return center, outers     