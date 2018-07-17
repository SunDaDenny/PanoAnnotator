import sys

import utils 
from .Scene import *
from .GeoPoint import *
from .WallPlane import *

class FloorPlane(object):

    def __init__(self, scene, isCeiling=False):

        self.__mainScene = scene

        self.__isCeiling = isCeiling

        self.geoPoints = scene.label.getLayoutPoints()
        self.walls = scene.label.getLayoutWalls()
        
        if not isCeiling:
            self.normal = (0, 1, 0)
            self.planeEquation = (0, 1, 0, 0)
        else:
            self.normal = (0, -1, 0)
            self.planeEquation = (0, -1, 0, 0)

        self.mesh = []
        self.meshProj = []

        self.init()

    def init(self):
    
        self.calcMeshByPoints()
    
    def calcMeshByPoints(self):

        self.mesh = []
        self.meshProj = []

        gps = self.geoPoints
        cameraH = self.__mainScene.label.getCameraHeight()
        cam2ceilH =  self.__mainScene.label.getCam2CeilHeight()

        if not self.__isCeiling:
            self.planeEquation = self.normal + (cameraH,)
            for gp in gps:
                self.mesh.append((gp.xyz[0], -cameraH, gp.xyz[2]))
        else:
            self.planeEquation = self.normal + (-cam2ceilH,)
            for gp in gps:
                self.mesh.append((gp.xyz[0], cam2ceilH, gp.xyz[2]))

        self.meshProj = utils.mesh2pano(self.mesh)

    def isCeiling(self):
        return self.__isCeiling

