
import os
import sys
import numpy as np
from PIL import Image as Image
import matplotlib.pyplot as plt

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import configs
import estimator
import data

class Scene(object):

    def __init__(self):
        
        ### Flag
        self.__isAvailable = False

        ### Pano Color Var
        self.__panoColorPath = ""
        self.__panoColorImage = None #(w,h)
        self.__panoColorData = None #(h,w)
        self.__panoColorPixmap = None

        ### Pano Depth Var
        self.__panoDepthPath = ""
        self.__panoDepthImage = None #(w,h)
        self.__panoDepthData = None #(h,w)

        self.__panoPointCloud = None

        self.label = data.Annotation(self)
        self.depthPred = None

        self.selectObjs = []

    def initScene(self, filePath, depthPred=None):

        self.setPanoColorPath(filePath)
        ### Load panorama, time consuming
        self.__panoColorImage = Image.open(filePath)
        self.__panoColorPixmap = QPixmap(filePath)
        self.__setPanoColorByImage(self.__panoColorImage)

        self.depthPred = depthPred

        fileDirPath = os.path.dirname(os.path.realpath(filePath))
        panoDepthPath = os.path.join(fileDirPath, configs.Params.depthFileDefaultName)
        
        if os.path.exists(panoDepthPath):
            self.__panoDepthPath = panoDepthPath
            self.__panoDepthImage = Image.open(panoDepthPath)
            self.__calcPanoDepthByImage(self.__panoDepthImage)
        else :
            print("No default depth image found")
            self.__calcPanoDepthByPred()
        
        self.label.calcInitLayout()

        self.__checkIsAvailable()

        return self.isAvailable()


    def __setPanoColorByImage(self, colorImage):
        colorData = np.asarray(colorImage)
        self.__panoColorData = colorData
    
    def __calcPanoDepthByImage(self, depthImage):
        depthData = np.asarray(depthImage)
        depthData = depthData.astype(float) / 4000 #For Matterport3d GT
        self.__panoDepthData = depthData
    
    def __calcPanoDepthByPred(self):
        pred = self.depthPred.predict(self.__panoColorImage)
        self.__panoDepthData = pred


    #####
    #Getter & Setter
    #####

    #Available
    def __checkIsAvailable(self):

        if self.__panoColorImage and (self.__panoDepthData is not None):
            self.__isAvailable = True
        else :
            self.__isAvailable = False
    
    def isAvailable(self):
        return self.__isAvailable

    #Pano Color
    def setPanoColorPath(self, filePath):
        self.__panoColorPath = filePath
        return self.__panoColorPath
    def getPanoColorPath(self):
        return self.__panoColorPath

    def getPanoColorImage(self):
        return self.__panoColorImage

    def getPanoColorPixmap(self):
        return self.__panoColorPixmap
    
    def getPanoColorData(self):
        return self.__panoColorData

    #Pano Depth
    def setPanoDepthPath(self, filePath):
        self.__panoDepthPath = filePath
        return self.__panoDepthPath
    def getPanoDepthPath(self):
        return self.__panoDepthPath

    def getPanoDepthData(self):
        return self.__panoDepthData


    #Pano Point Cloud
    def setPanoPointCloud(self, pc):
        self.__panoPointCloud = pc
        return self.__panoPointCloud
    def getPanoPointCloud(self):
        return self.__panoPointCloud

    def getSelectObjs(self, objType=None):
        objs = []
        typeDict = {'GeoPoint':data.GeoPoint, 'WallPlane':data.WallPlane, 
                    'FloorPlane':data.FloorPlane}
        if objType:
            for obj in self.selectObjs:
                if type(obj) == typeDict[objType]:
                    objs.append(obj)
            return objs
        elif objType == None:
            return self.selectObjs
        
    

