import numpy as np

import matplotlib.pyplot as pyplot
from skimage import transform

import data
import utils

class PushPredLite(object):

    def __init__(self, scene):
        
        self.__scene = scene
        self.size = [128, 256, 3]#[256, 512, 3]

    def optimizeWall(self, wall, val):

        dist = abs(wall.planeEquation[3]) / 10
        step = dist if val >= 0 else -dist

        sampleList = [step*(i+1) for i in range(5)]

        errList = []
        tmpPlane = self.genTmpWall(wall)
        for step in sampleList:
            tmpPlane.moveByNormal(step)
            err = self.calcMapError(tmpPlane)
            errList.append(err)
        minVal = min(errList)
        minIdx = errList.index(minVal)
        moveVal = sampleList[minIdx]

        self.__scene.label.moveWallByNormal(wall, moveVal)

    def genTmpWall(self, wall):

        gp1 = data.GeoPoint(self.__scene, None, wall.gPoints[0].xyz)
        gp2 = data.GeoPoint(self.__scene, None, wall.gPoints[1].xyz)
        wall = data.WallPlane(self.__scene, [gp1, gp2])

        return wall

    def genEdgeMap(self, wall):

        edgeMap = np.zeros(self.size)
        utils.imageDrawWallEdge(edgeMap, wall)
        edgeMapDilation = utils.imageDilation(edgeMap, 1)
        edgeMapBlur = utils.imageGaussianBlur(edgeMapDilation, 2)

        return edgeMapBlur

    def genNormalMap(self, wall):

        normalMap = np.zeros(self.size)
        utils.imageDrawWallFace(normalMap, wall)

        return normalMap

    def genBbox2d(self, wall):

        size = (self.size[0], self.size[1])
        sizeT = utils.posTranspose(size)
        extend = 10

        bbox = wall.bbox2d
        poslt = utils.posTranspose(utils.coords2pos(bbox[0], sizeT))
        posrb = utils.posTranspose(utils.coords2pos(bbox[1], sizeT))

        poslt = (poslt[0] - extend, poslt[1] - extend)
        poslt = utils.checkImageBoundary(poslt, size)
        posrb = (posrb[0] + extend, posrb[1] + extend)
        posrb = utils.checkImageBoundary(posrb, size)

        return poslt, posrb

    def calcMapError(self, wall):
        
        size = (self.size[0], self.size[1])
        poslt, posrb = self.genBbox2d(wall)

        normalMap = self.genNormalMap(wall)
        normalMapRoi = utils.imageROI(normalMap, poslt, posrb)
        
        oMap = self.__scene.getPanoOmapData()
        oMapR = utils.imageResize(oMap, size)
        oMapRoi = utils.imageROI(oMapR, poslt, posrb)

        omapMSE = utils.imagesMSE(normalMapRoi, oMapRoi, size)

        edgeMap = self.genEdgeMap(wall)
        edgeMapRoi = utils.imageROI(edgeMap, poslt, posrb)

        linesMap = self.__scene.getPanoLinesData()
        linesMapR = utils.imageResize(linesMap, size)
        linesMapRoi = utils.imageROI(linesMapR, poslt, posrb)

        lineMSE = utils.imagesMSE(edgeMapRoi, linesMapRoi, size)

        #utils.showImage(edgeMapRoi)
        #utils.showImage(linesMapRoi)
        #print('MSE lines:{0:.3f}  normal:{1:.3f}'.format(lineMSE,omapMSE))

        mix = omapMSE + lineMSE
        return mix