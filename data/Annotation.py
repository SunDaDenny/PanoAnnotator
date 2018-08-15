import numpy as np

import data
import utils
import configs.Params as pm
import estimator

class Annotation(object):

    def __init__(self, scene):
        
        self.__scene = scene
        #self.pushPred = estimator.PushPredLite(scene)
        self.pushPred = estimator.PushPred(scene)

        self.__layoutPoints = []
        self.__layoutWalls = []

        self.__layoutFloor = None
        self.__layoutCeiling = None

        self.__cameraHeight = pm.defaultCameraHeight
        self.__layoutHeight = pm.defaultLayoutHeight

        self.__layoutEdgeMap = None
        self.__layoutNormalMap = None

    #####
    #Layout generation
    #####
    def genLayoutWallsByPoints(self, points):

        self.__layoutWalls = []
        self.__scene.selectObjs = []

        pnum = len(points)
        for i in range(0, pnum):
            plane = data.WallPlane(self.__scene, 
                             [points[i], points[(i+1)%pnum]])
            self.__layoutWalls.append(plane)
       
        self.__layoutFloor = data.FloorPlane(self.__scene, False)
        self.__layoutCeiling = data.FloorPlane(self.__scene, True)

    def calcManhLayoutPoints(self, points):

        self.__layoutPoints = []

        manhxyz = utils.alignManhattan(points)     
        for xyz in manhxyz:
            gp = data.GeoPoint(self.__scene, None, xyz)
            self.__layoutPoints.append(gp)

    def genManhLayoutWalls(self):
        
        self.__layoutWalls = [] 

        self.calcManhLayoutPoints(self.__layoutPoints)
        self.genLayoutWallsByPoints(self.__layoutPoints)
    
    def genSplitPoints(self,wall, point):

        p1 = data.GeoPoint(self.__scene, None, point)
        p2 = data.GeoPoint(self.__scene, None, point)

        wP1idx = self.__layoutPoints.index(wall.gPoints[0])
        wP2idx = self.__layoutPoints.index(wall.gPoints[1])

        if abs(wP1idx - wP2idx) == len(self.__layoutPoints) - 1: 
            self.__layoutPoints.extend((p1, p2))
        else:
            idx = max([wP1idx,wP2idx])
            self.__layoutPoints[idx:idx] = [p1, p2]
            
        self.genLayoutWallsByPoints(self.__layoutPoints)

    #####
    #Layout operation
    #####
    def addLayoutPoint(self, point):

        if type(point) is data.GeoPoint:
            for i, gp in enumerate(self.__layoutPoints):
                if gp.coords[0] > point.coords[0]:
                    self.__layoutPoints.insert(i, point)
                    self.genLayoutWallsByPoints(self.__layoutPoints)
                    return
            self.__layoutPoints.append(point)
            self.genLayoutWallsByPoints(self.__layoutPoints)
        else :
            print("Type error")

    def delLayoutPoint(self, point):

        if point in self.__layoutPoints:
            self.__layoutPoints.remove(point)
            self.genLayoutWallsByPoints(self.__layoutPoints)

    def delLastLayoutPoints(self):
        
        if self.__layoutPoints:
            tmp = self.__layoutPoints[:]
            tmp.sort(key=lambda x:x.id)
            delPoint = tmp.pop()
            self.__layoutPoints.remove(delPoint)
            self.genLayoutWallsByPoints(self.__layoutPoints)

    def delLayoutWalls(self, walls):

        for wall in walls:
            if wall in self.__layoutWalls:
                for point in wall.gPoints:
                    if point in self.__layoutPoints:
                        self.__layoutPoints.remove(point)
        self.genManhLayoutWalls()

    def mergeLayoutWalls(self, walls):

        gps = []
        for wall in walls:
            for point in wall.gPoints:
                if point not in gps:
                    gps.append(point)
                elif point in self.__layoutPoints:
                    self.__layoutPoints.remove(point)
        self.genManhLayoutWalls()

    def mergeTrivialWalls(self):

        delWalls = []
        for wall in self.__layoutWalls:
            gps = wall.gPoints
            if utils.pointsDistance(gps[0].xyz, gps[1].xyz) < 0.5:
                delWalls.append(wall)
        self.delLayoutWalls(delWalls)

    def cleanLayout(self):

        self.__layoutPoints = []
        self.__layoutWalls = []
        
        self.__layoutFloor = None
        self.__layoutCeiling = None
        self.__cameraHeight = pm.defaultCameraHeight
        self.__layoutHeight = pm.defaultLayoutHeight
    
    #####
    # Objects manual operation
    #####
    def moveWallByNormal(self, wall, val):

        wall.moveByNormal(val)
        self.updateLayoutGeometry()
    
    def moveFloor(self, val):
        self.__cameraHeight += val
        self.__layoutHeight += val
        self.updateLayoutGeometry()
    
    def moveCeiling(self, val):
        self.__layoutHeight += val
        self.updateLayoutGeometry()

    #####
    # Objects automatic operation
    #####
    def moveWallByPred(self, wall, val):
        self.pushPred.optimizeWall(wall, val)

    #####
    # Auto-Calulation part
    #####
    def calcLayoutHeight(self):
        
        def calcPartHeight(range, step):
            tmpList = []
            for i in np.arange(0.0, 1.0, 0.01):
                for j in np.arange(range[0], range[1], step):
                    tmpGp = data.GeoPoint(self.__scene, (i,j))
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
        #self.calcLayoutHeight()

        samplePoints = []
        for x in np.arange(0.0, 1.0, 0.01):
            coords = (x, 0.5)
            geoPoint = data.GeoPoint(self.__scene, coords)
            samplePoints.append(geoPoint)
        
        self.calcManhLayoutPoints(samplePoints)
        self.genLayoutWallsByPoints(self.__layoutPoints)

        self.mergeTrivialWalls()
        self.pushPred.optimizeLayout()
        self.mergeTrivialWalls()

    def updateLayoutGeometry(self):

        for wall in self.__layoutWalls:
            wall.updateGeometry()
        self.__layoutFloor.updateGeometry()
        self.__layoutCeiling.updateGeometry()


    '''
    def calcLayoutMap(self):

        size = [256, 512, 3]
        #size = [128, 256, 3]

        #Edge map
        edgeMap = np.zeros(size)
        for wall in self.__layoutWalls:
            utils.imageDrawWallEdge(edgeMap, wall)
        self.__layoutEdgeMap = edgeMap

        edgeMapDilation = utils.imageDilation(edgeMap, 1)
        edgeMapBlur = utils.imageGaussianBlur(edgeMapDilation, 2)
        self.__layoutEdgeMap = edgeMapBlur

        edgeMapPixmap = utils.data2Pixmap(self.__layoutEdgeMap)
        self.__scene.setLayoutEdgeMapPixmap(edgeMapPixmap)
    
        #Normal map
        normalMap = np.zeros(size)
        normalMap[:,:,0] = 1

        for wall in self.__layoutWalls:
            utils.imageDrawWallFace(normalMap, wall)
        self.__layoutNormalMap = normalMap

        normalMapPixmap = utils.data2Pixmap(self.__layoutNormalMap)
        self.__scene.setLayoutNormalMapPixmap(normalMapPixmap)
    '''

    #####
    #Getter & Setter
    #####
    def setCameraHeight(self, cameraH):
        self.__cameraHeight = cameraH

    def setLayoutHeight(self, layoutH):
        self.__layoutHeight = layoutH

    def getLayoutPoints(self):
        return self.__layoutPoints

    def getLayoutWalls(self):
        return self.__layoutWalls
    
    def getLayoutFloor(self):
        return self.__layoutFloor

    def getLayoutCeiling(self):
        return self.__layoutCeiling

    def getLayoutEdgeMap(self):
        return self.__layoutEdgeMap
    
    def getLayoutNormalMap(self):
        return self.__layoutNormalMap

    def getCameraHeight(self):
        return self.__cameraHeight

    def getCam2CeilHeight(self):
        return self.__layoutHeight - self.__cameraHeight

    def getLayoutHeight(self):
        return self.__layoutHeight
