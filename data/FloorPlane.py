import sys

import utils 
from .Scene import *
from .GeoPoint import *
from .WallPlane import *

class FloorPlane(object):

    def __init__(self, scene, isCeiling=False):

        self.__mainScene = scene

        self.__isCeiling = isCeiling

        self.gPoints = scene.label.getLayoutPoints()
        self.walls = scene.label.getLayoutWalls()
        
        self.normal = (0, -1, 0) if isCeiling else (0, 1, 0)
        self.height = 0
        self.planeEquation = (0, 0, 0, 0)

        self.corners = []
        self.edges = []

        self.init()

    def init(self):
    
        self.updateGeometry()
    
    def updateGeometry(self):

        cameraH = self.__mainScene.label.getCameraHeight()
        cam2ceilH =  self.__mainScene.label.getCam2CeilHeight()
        self.height = cam2ceilH if self.__isCeiling else -cameraH 
        self.planeEquation = self.normal + (-self.height,)

        self.updateCorners()
        self.updateEdges()
        
    def updateCorners(self):

        self.corners = []
        for gp in self.gPoints:
            xyz = (gp.xyz[0], self.height, gp.xyz[2])
            corner = data.GeoPoint(self.__mainScene, None, xyz)
            self.corners.append(corner)
    
    def updateEdges(self):
        
        self.edges = []
        cnum = len(self.corners)
        for i in range(cnum):
            edge = data.GeoEdge(self.__mainScene, 
                                (self.corners[i], self.corners[(i+1)%cnum]))
            self.edges.append(edge)


    def isCeiling(self):
        return self.__isCeiling

