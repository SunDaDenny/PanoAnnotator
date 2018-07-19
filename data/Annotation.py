
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
        self.__layoutCeiling = None

        self.__cameraHeight = pm.defaultCameraHeight
        self.__layoutHeight = pm.defaultLayoutHeight

    #####
    #Layout generation
    #####
    def genLayoutWallsByPoints(self, points):

        self.__layoutWalls = []
        self.__mainScene.selectObjs = []

        #test
        #self.calcManhLayoutPoints(points)
        #points = self.__layoutPoints

        pnum = len(points)
        for i in range(0, pnum):
            plane = WallPlane(self.__mainScene, 
                             [points[i], points[(i+1)%pnum]])
            self.__layoutWalls.append(plane)
       
        self.__layoutFloor = FloorPlane(self.__mainScene, False)
        self.__layoutCeiling = FloorPlane(self.__mainScene, True)
        

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
            vec1 = tuple(np.array(walls[0].normal)*-0.5)
            vec2 = tuple(np.array(walls[1].normal)*-0.5)
            concave1 = GeoPoint(self.__mainScene, None, utils.vectorAdd(center.xyz,vec1))
            concave2 = GeoPoint(self.__mainScene, None, utils.vectorAdd(center.xyz,vec2))
            vec3 = utils.vectorAdd(vec1,vec2)
            convex = GeoPoint(self.__mainScene, None, utils.vectorAdd(center.xyz,vec3))

            idx = self.__layoutPoints.index(center)
            self.delLayoutPoint(center)
            self.__layoutPoints[idx:idx] = [concave1, convex ,concave2]
            
            self.genManhLayoutWalls()
    
    def genSplitPoints(self,wall, point):

        p1 = data.GeoPoint(self.__mainScene, None, point)
        p2 = data.GeoPoint(self.__mainScene, None, point)

        wP1idx = self.__layoutPoints.index(wall.geoPoints[0])
        wP2idx = self.__layoutPoints.index(wall.geoPoints[1])

        if abs(wP1idx - wP2idx) == len(self.__layoutPoints) - 1:
            self.__layoutPoints.extend((p1, p2))
        else:
            idx = max([wP1idx,wP2idx])
            self.__layoutPoints[idx:idx] = [p1, p2]
            
        self.genLayoutWallsByPoints(self.__layoutPoints)

    #####
    #Data list operation
    #####
    def addLayoutPoint(self, point):

        if type(point) is GeoPoint:
            for i, gp in enumerate(self.__layoutPoints):
                if gp.coords[0] > point.coords[0]:
                    self.__layoutPoints.insert(i, point)
                    self.genLayoutWallsByPoints(self.__layoutPoints)
                    return
            self.__layoutPoints.append(point)
            self.genLayoutWallsByPoints(self.__layoutPoints)
        else :
            print("Type error")

    def delLastLayoutPoints(self):
        
        if self.__layoutPoints:
            tmp = self.__layoutPoints[:]
            tmp.sort(key=lambda x:x.id)
            delPoint = tmp.pop()
            self.__layoutPoints.remove(delPoint)

            self.genLayoutWallsByPoints(self.__layoutPoints)

    def delLayoutPoint(self, point):

        if point in self.__layoutPoints:
            self.__layoutPoints.remove(point)
            self.genLayoutWallsByPoints(self.__layoutPoints)
    
    def delLayoutWalls(self, walls):

        for wall in walls:
            if wall in self.__layoutWalls:
                for point in wall.geoPoints:
                    if point in self.__layoutPoints:
                        self.__layoutPoints.remove(point)
        #self.genLayoutWallsByPoints(self.__layoutPoints)
        self.genManhLayoutWalls()

    def mergeLayoutWalls(self, walls):

        gps = []
        for wall in walls:
            for point in wall.geoPoints:
                if point not in gps:
                    gps.append(point)
                elif point in self.__layoutPoints:
                    self.__layoutPoints.remove(point)

        #self.genLayoutWallsByPoints(self.__layoutPoints)
        self.genManhLayoutWalls()

    def moveWallByNormal(self, wall, val):

        wall.moveByNormal(val)
        self.calcLayoutMesh()

    def cleanLayout(self):

        self.__layoutPoints = []
        self.__layoutWalls = []
        
        self.__layoutFloor = None
        self.__layoutCeiling = None
        #self.__cameraHeight = pm.defaultCameraHeight
        #self.__layoutHeight = pm.defaultLayoutHeight
        
    
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
        
        self.calcManhLayoutPoints(samplePoints)
        self.genLayoutWallsByPoints(self.__layoutPoints)

    def calcLayoutMesh(self):
        for wall in self.__layoutWalls:
            wall.calcMeshByPoints()
        self.__layoutFloor.calcMeshByPoints()
        self.__layoutCeiling.calcMeshByPoints()
    
    #####
    #Getter & Setter
    #####
    def setCameraHeight(self, cameraheight):
        self.__cameraHeight = cameraheight
        self.calcLayoutMesh()

    def setLayoutHeight(self, layoutHeight):
        self.__layoutHeight = layoutHeight
        self.calcLayoutMesh()

    def getLayoutPoints(self):
        return self.__layoutPoints

    def getLayoutWalls(self):
        return self.__layoutWalls
    
    def getLayoutFloor(self):
        return self.__layoutFloor

    def getLayoutCeiling(self):
        return self.__layoutCeiling

    def getCameraHeight(self):
        return self.__cameraHeight

    def getCam2CeilHeight(self):
        return self.__layoutHeight - self.__cameraHeight

    def getLayoutHeight(self):
        return self.__layoutHeight