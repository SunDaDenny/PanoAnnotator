
import sys
import math

import utils 
from .Scene import *
from .Annotation import *

gpInstanceCount = 0

class GeoPoint(object):

    def __init__(self, scene, coords=None, xyz=None):

        self.__scene = scene

        self.coords = coords
        self.color = (0, 0, 0)
        self.depth = 0
        self.xyz = xyz

        self.type = 0 # [convex, concave, occul]
        self.order = 0

        self.initByScene()

    def __hash__(self):
        return hash((self.order))
    
    def __eq__(self, other):
        return (self.order) == (other.order)

    def initByScene(self):

        if self.coords == None:
            self.coords = utils.xyz2coords(self.xyz)

        coordsT = (self.coords[1], self.coords[0])

        colorData = self.__scene.getPanoColorData()

        colorPos = utils.coords2pos(coordsT, colorData.shape)
        rgb = colorData[colorPos[0]][colorPos[1]]
        self.color = (rgb[0], rgb[1], rgb[2])

        depthData = self.__scene.getPanoDepthData()
        
        depthPos = utils.coords2pos(coordsT, depthData.shape)
        avgVal= utils.calcCenterRegionAvgVal(depthData, 
                                                            depthPos, (5, 5))
        self.depth = avgVal
        #self.depth = depthData[depthPos[0]][depthPos[1]]

        if self.xyz == None:
            self.xyz = utils.coords2xyz(self.coords, self.depth)
        
        global gpInstanceCount
        gpInstanceCount += 1
        self.order = gpInstanceCount

        #self.calcGeometryType()

    def moveByVector(self, vec):
        self.xyz = (self.xyz[0] + vec[0], 
                    self.xyz[1] + vec[1], 
                    self.xyz[2] + vec[2])
        self.coords = utils.xyz2coords(self.xyz)

    def calcGeometryType(self):

        coordsT = (self.coords[1], self.coords[0])
        depthData = self.__scene.getPanoDepthData()

        depthPos = utils.coords2pos(coordsT, depthData.shape)
        depth = depthData[depthPos[0]][depthPos[1]]
        if depth <= 0:
            return

        #print(depthPos)
        lt, rb = utils.calcCenterRegionPos(depthPos, 
                                            ( int(50/depth), int(50/depth))
                                            ,depthData.shape)
        #print("{0} {1}".format(lt, rb))
        
        cb = (rb[0], depthPos[1])
        #print("cb {0}".format(cb))
        regionL = utils.getRegionData(depthData, lt, cb)
        #print(regionL.shape)
        ct = (lt[0], depthPos[1])
        #print("ct {0}".format(ct))
        regionR = utils.getRegionData(depthData, ct, rb)
        #print(regionR.shape)

        avgL = np.nanmean(regionL)
        avgR = np.nanmean(regionR)

        #print("L : {0}   R : {1}".format(avgL, avgR))
        if abs(avgL - avgR) > 0.75:
            self.type = 2

    def getDistance(self, point):

        dx = math.pow(point.xyz[0] - self.xyz[0], 2)
        dy = math.pow(point.xyz[1] - self.xyz[1], 2)
        dz = math.pow(point.xyz[2] - self.xyz[2], 2)
        dist = (dx, dy, dz)

        return dist

    def getPointsAvg(self, points):

        avg = list(self.xyz)
        for p in points:
            for i in range(3):
                avg[i] = avg[i] + p.xyz[i]
        for i in range(3):
            avg[i] = avg[i]/ (len(points)+1)
        
        return tuple(avg)

    