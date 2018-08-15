import numpy as np

import data
import utils

class PushPred(object):

    def __init__(self, scene):

        self.__isAvailable = False
        self.__scene = scene

        self.__size = [128, 256, 3] #[256, 512, 3]

        self.__progCount = 0

    def optimizeWall(self, wall, val):

        dist = abs(wall.planeEquation[3]) / 10
        step = dist if val >= 0 else -dist
        
        utils.resetProgress(self.__scene, 5)
        sampleList = [step*(i+1) for i in range(5)]

        moveVal = self.iterateSampleWall(wall, sampleList)
        self.__scene.label.moveWallByNormal(wall, moveVal)

    def optimizeLayout(self):
        
        walls = self.__scene.label.getLayoutWalls()
        calcNum = 6 + 6 + len(walls) * 5
        utils.resetProgress(self.__scene, calcNum)

        sampleList = [0, 0.1, 0.2, 0.3, 0.4, 0.5]
        moveVal = self.iterateSampleFloor(sampleList, True)
        self.__scene.label.moveFloor(moveVal)

        sampleList = [0, 0.1, 0.2, 0.3, 0.4, 0.5]
        moveVal = self.iterateSampleFloor(sampleList, False)
        self.__scene.label.moveCeiling(moveVal)

        for wall in walls:

            dist = abs(wall.planeEquation[3]) / 10
            sampleList = [0, 1*dist, 2*dist, 3*dist, -1*dist]
            #sampleList = [0, 1*dist, 2*dist, 3*dist, -1*dist, -2*dist, -3*dist]
            #sampleList = [0, 1*dist, 2*dist, 3*dist, 4*dist, 5*dist, 6*dist, -1*dist]

            moveVal = self.iterateSampleWall(wall, sampleList)
            self.__scene.label.moveWallByNormal(wall, moveVal)
        
    def iterateSampleWall(self, wall, sampleList):

        errList = []
        for step in sampleList:
            self.__scene.label.moveWallByNormal(wall, step)
            errList.append(self.calcMapError())
            self.__scene.label.moveWallByNormal(wall, -step)
        minIdx = errList.index(min(errList))
        moveVal = sampleList[minIdx]

        return moveVal

    def iterateSampleFloor(self, sampleList, isfloor=True):

        errList = []
        for step in sampleList:
            if isfloor:
                self.__scene.label.moveFloor(step)
                errList.append(self.calcMapError())
                self.__scene.label.moveFloor(-step)
            else:
                self.__scene.label.moveCeiling(step)
                errList.append(self.calcMapError())
                self.__scene.label.moveCeiling(-step)
        minIdx = errList.index(min(errList))
        moveVal = sampleList[minIdx]

        return moveVal

    def genEdgeMap(self):

        edgeMap = np.zeros(self.__size)
        for wall in  self.__scene.label.getLayoutWalls():
            utils.imageDrawWallEdge(edgeMap, wall)
        edgeMapDilation = utils.imageDilation(edgeMap, 1)
        edgeMapBlur = utils.imageGaussianBlur(edgeMapDilation, 2)

        return edgeMapBlur

    def genNormalMap(self):

        normalMap = np.zeros(self.__size)
        normalMap[:,:,0] = 1
        for wall in  self.__scene.label.getLayoutWalls():
            utils.imageDrawWallFace(normalMap, wall)

        return normalMap

    def calcMapError(self):
        
        size = (self.__size[0], self.__size[1])
        
        normalMap = self.genNormalMap()
        oMap = self.__scene.getPanoOmapData()
        oMapR = utils.imageResize(oMap, size)
        
        omapMSE = utils.imagesMSE(normalMap, oMapR, size)

        edgeMap = self.genEdgeMap()
        linesMap = self.__scene.getPanoLinesData()
        linesMapR = utils.imageResize(linesMap, size)

        lineMSE = utils.imagesMSE(edgeMap, linesMapR, size) 

        #utils.showImage(edgeMap)
        #utils.showImage(normalMap)
        #utils.showImage(linesMapR)
        #utils.showImage(oMapR)
        #print('MSE lines:{0:.3f}  normal:{1:.3f}'.format(lineMSE,omapMSE))
        #print('MSE normal:{0:.3f}'.format(omapMSE))
        #print('MSE normal:{0:.3f}'.format(lineMSE))
        utils.updateProgress(self.__scene)

        mix = omapMSE  + lineMSE * 10
        return mix

