import sys

import utils 
from .Scene import *
from .GeoPoint import *
from .WallPlane import *

class FloorPlane(object):

    def __init__(self, scene):

        self.__mainScene = scene

        self.geoPoints = scene.label.getLayoutPoints()
        self.walls = scene.label.getLayoutWalls()
        
        self.normal = (0, 1, 0)
        self.planeEquation = (0, 1, 0, 0) 

        self.mesh = []
        self.meshProj = []

        self.init()

    def init(self):
    
        self.calcMeshByPoints()
    
    def calcMeshByPoints(self):

        gps = self.geoPoints
        cameraH = self.__mainScene.label.getCameraHeight()

        self.planeEquation = self.normal + (cameraH,)

        for gp in gps:
            self.mesh.append((gp.xyz[0], -cameraH, gp.xyz[2]))

        self.meshProj = utils.mesh2pano(self.mesh)

