
import sys
import math
import numpy as np

import utils
import configs.Params as pm
from .Scene import *
from .GeoPoint import *
from .WallPlane import *
from .FloorPlane import *

class Annotation(object):

    def __init__(self, scene):
        
        self.__mainScene = scene

        self.__layoutPoints = []
        self.__layoutWalls = []

        self.__layoutFloor = None

        self.__cameraHeight = pm.defaultCameraHeight
        self.__layoutHeight = pm.defaultLayoutHeight

    #####
    #Layout generation
    #####
    def genLayoutWallsByPoints(self, points):

        self.__layoutWalls = []

        pnum = len(points)
        for i in range(0, pnum):
            plane = WallPlane(self.__mainScene, 
                             [points[i], points[(i+1)%pnum]])
            self.__layoutWalls.append(plane)
        

    def calcManhLayoutPoints(self, points):

        self.__layoutPoints = []

        manhxyz = utils.alignManhattan(points)     
        for xyz in manhxyz:
            gp = GeoPoint(self.__mainScene, None, xyz)
            self.__layoutPoints.append(gp)

    def genManhLayoutWalls(self):
        
        self.__layoutWalls = [] 

        self.calcManhLayoutPoints(self.__layoutPoints)
        self.genLayoutWallsByPoints(self.__layoutPoints)

    def genConvexPoints(self, walls):

        if len(walls) < 2:
            print("wall numbers must be 2")
            return

        center, outers = walls[0].getConnectPoint(walls[1])
        if center:
            concave1 = GeoPoint(self.__mainScene, None, center.xyz)
            concave2 = GeoPoint(self.__mainScene, None, center.xyz)
            convex = GeoPoint(self.__mainScene, None, center.xyz)
            vec1 = tuple(np.array(walls[0].normal)*-0.5)
            vec2 = tuple(np.array(walls[1].normal)*-0.5)
            concave1.moveByVector(vec1)
            concave2.moveByVector(vec2)
            convex.moveByVector(utils.vectorAdd(vec1,vec2))

            self.delLayoutPoint(center)
            self.__layoutPoints.append(concave1)
            self.__layoutPoints.append(concave2)
            self.__layoutPoints.append(convex)
            self.__layoutPoints.sort(key=lambda x:x.coords[0])
            self.genManhLayoutWalls()
            

    #####
    #Data list operation
    #####
    def addLayoutPoint(self, point):

        self.__isClose = False
        if type(point) is GeoPoint:
            self.__layoutPoints.append(point)
            self.__layoutPoints.sort(key=lambda x:x.coords[0])
            self.genLayoutWallsByPoints(self.__layoutPoints)
        else :
            print("Type error")

    def delLastLayoutPoints(self):
        
        self.__isClose = False
        if self.__layoutPoints:
            self.__layoutPoints.sort(key=lambda x:x.order)
            self.__layoutPoints.pop()
            self.__layoutPoints.sort(key=lambda x:x.coords[0])
            self.genLayoutWallsByPoints(self.__layoutPoints)

    def delLayoutPoint(self, point):

        self.__isClose = False
        if point in self.__layoutPoints:
            self.__layoutPoints.remove(point)
            self.genLayoutWallsByPoints(self.__layoutPoints)
    
    def delLayoutWalls(self, walls):

        self.__isClose = False
        for wall in walls:
            if not type(wall) == WallPlane:
                continue
            if wall in self.__layoutWalls:
                for point in wall.geoPoints:
                    if point in self.__layoutPoints:
                        self.__layoutPoints.remove(point)
        self.genLayoutWallsByPoints(self.__layoutPoints)

    def mergeLayoutWalls(self, walls):

        self.__isClose = False
        gps = []
        for wall in walls:
            if not type(wall) == WallPlane:
                continue
            for point in wall.geoPoints:
                if point not in gps:
                    gps.append(point)
                elif point in self.__layoutPoints:
                    self.__layoutPoints.remove(point)

        self.genLayoutWallsByPoints(self.__layoutPoints)


    def cleanLayout(self):

        self.__layoutPoints = []
        self.__layoutWalls = []

        #self.__cameraHeight = pm.defaultCameraHeight
        #self.__layoutHeight = pm.defaultLayoutHeight
        
        self.__isClosed = False
    
    #####
    # Auto-Calulation part
    #####
    def calcLayoutHeight(self):
        
        def calcPartHeight(range, step):
            tmpList = []
            for i in np.arange(0.0, 1.0, 0.01):
                for j in np.arange(range[0], range[1], step):
                    tmpGp = GeoPoint(self.__mainScene, (i,j))
                    if not tmpGp.xyz[1] == 0:
                        tmpList.append(tmpGp.xyz[1])
            return np.mean(tmpList)

        cam2ceil = calcPartHeight((0.0, pm.layoutHeightSampleRange), 
                                  pm.layoutHeightSampleStep)
        cam2floor = calcPartHeight((1.0 - pm.layoutHeightSampleRange, 1.0), 
                                  pm.layoutHeightSampleStep)

        self.__cameraHeight = abs(cam2floor)
        self.__layoutHeight = cam2ceil + self.__cameraHeight

    def calcInitLayout(self):
        
        self.cleanLayout()
        self.calcLayoutHeight()

        samplePoints = []
        for x in np.arange(0.0, 1.0, 0.01):
            coords = (x, 0.5)
            geoPoint = GeoPoint(self.__mainScene, coords)
            samplePoints.append(geoPoint)

        samplePoints.sort(key=lambda x:x.coords[0])
        
        self.calcManhLayoutPoints(samplePoints)
        self.genLayoutWallsByPoints(self.__layoutPoints)

    
    #####
    #Getter & Setter
    #####
    def setCameraHeight(self, cameraheight):
        self.__cameraHeight = cameraheight
        for wall in self.__layoutWalls:
            wall.calcMeshByPoints()

    def setLayoutHeight(self, layoutHeight):
        self.__layoutHeight = layoutHeight
        for wall in self.__layoutWalls:
            wall.calcMeshByPoints()
    
    def getLayoutPoints(self):
        return self.__layoutPoints

    def getLayoutWalls(self):
        return self.__layoutWalls
    
    def getLayoutFloor(self):
        return self.__layoutFloor

    def getCameraHeight(self):
        return self.__cameraHeight

    def getCam2CeilHeight(self):
        return self.__layoutHeight - self.__cameraHeight

    def getLayoutHeight(self):
        return self.__layoutHeight