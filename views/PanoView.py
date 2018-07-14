
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import data
import utils

class PanoView(QLabel):

    def __init__(self, parent=None):
        super(PanoView, self).__init__(parent)

        self.__isAvailable = False
        self.__mainWindow = None
        self.__mainScene = None

        self.__panoPixmap = QPixmap()

        self.__mode = 0 # 0:point select, 1/2:height modify , 3:plane modify
        self.__lastPos = QPoint()
        self.__isDrag = False

        self.isLayoutWallEnable = True
        self.isLayoutPointEnable = True
        self.isLayoutFinalWallEnable = False

    #####
    #Comstum Method
    #####
    def initByScene(self, scene):

        self.__mainScene = scene
        self.__panoPixmap = self.__mainScene.getPanoColorPixmap()

        self.__isAvailable = True

    def createGeoPoint(self, sceenPos):
        
        coords = utils.pos2coords(sceenPos, 
                                            (self.width(), self.height()))
        geoPoint = data.GeoPoint(self.__mainScene, coords)

        return geoPoint

    def modeSwitch(self, mode):

        if self.__mode == mode:
            self.__mode = 0
        else:
            self.__mode = mode

    def selectByCoords(self, coords):
        
        vec =  utils.coords2xyz(coords, 1)

        isHit = False
        for wall in self.__mainScene.label.getLayoutWalls():
            if wall.checkRayHit(vec):
                isHit = True
                if wall in self.__mainWindow.selectObjects:
                    self.__mainWindow.selectObjects.remove(wall) 
                else:
                    self.__mainWindow.selectObjects.append(wall)

    #####
    #Override
    #####
    def paintEvent(self, event):

        if self.__isAvailable:
            qp = QPainter()

            qp.begin(self)
            qp.drawPixmap(0, 0, self.width(), self.height(), self.__panoPixmap)

            pen = QPen(Qt.red, 1, Qt.SolidLine)
            qp.setPen(pen)

            if self.isLayoutPointEnable:

                for point in self.__mainScene.label.getLayoutPoints():

                    if point in self.__mainWindow.selectObjects:
                        pen = QPen(Qt.yellow, 2, Qt.SolidLine)
                    else:
                        pen = QPen(Qt.red, 2, Qt.SolidLine)
                    qp.setPen(pen)

                    pos = utils.coords2pos(point.coords, 
                                                    (self.width(), self.height()))
                    qp.drawEllipse(QPoint(pos[0], pos[1]), 5, 5)
                    #qp.drawLine(pos[0], 0, pos[0], self.height())
            
            if self.isLayoutWallEnable:

                def drawWallMeshProj(self, wall):
                    wallPoints = wall.meshProj
                    pnum = len(wallPoints)
                    for i in range(pnum):
                        pos1 = utils.coords2pos(wallPoints[i], 
                                                        (self.width(), self.height()))
                        pos2 = utils.coords2pos(wallPoints[(i+1)%pnum], 
                                                        (self.width(), self.height()))
                        if abs(pos1[0] - pos2[0]) > self.width()/10:
                            continue
                        qp.drawLine(pos1[0], pos1[1], pos2[0], pos2[1])                 

                for wall in self.__mainScene.label.getLayoutWalls():           
                    if wall not in self.__mainWindow.selectObjects:
                        pen = QPen(Qt.blue, 2, Qt.SolidLine)
                        qp.setPen(pen)
                        drawWallMeshProj(self, wall)
                
                for wall in self.__mainScene.label.getLayoutWalls():
                    if wall in self.__mainWindow.selectObjects:
                        pen = QPen(Qt.yellow, 2, Qt.SolidLine)
                        qp.setPen(pen)
                        drawWallMeshProj(self, wall)             
                    
            qp.end()

        self.__mainWindow.updateViews()

    def mousePressEvent(self, event):
        self.__lastPos = event.pos()

    def mouseMoveEvent(self, event):
        
        self.__isDrag = True

        dx = event.x() - self.__lastPos.x()
        dy = event.y() - self.__lastPos.y()

        if event.buttons() == Qt.LeftButton:
            if self.__mode == 1:
                newH = self.__mainScene.label.getCameraHeight() + float(dy)/1000
                self.__mainScene.label.setCameraHeight(newH)
            elif self.__mode == 2:
                newH = self.__mainScene.label.getLayoutHeight() - float(dy)/1000
                self.__mainScene.label.setLayoutHeight(newH)

        self.__mainWindow.updateViews()

    def mouseReleaseEvent(self, event):
        #print("point : {0} {1}".format(event.pos().x(), event.pos().y()))
        screenPos = (event.pos().x(),event.pos().y())
        if self.__isAvailable:
            if not self.__isDrag and self.__mode == 0:
                if event.button() == Qt.LeftButton:
                        
                    geoPoint = self.createGeoPoint(screenPos)
                    self.__mainScene.label.addLayoutPoint(geoPoint)
                    self.__mainWindow.updateListView()

                elif event.button() == Qt.RightButton:
                    self.__mainScene.label.delLastLayoutPoints()
                    self.__mainWindow.updateListView()
                    
            elif self.__mode == 3:
                self.selectByCoords((event.x()/self.width(),
                                    event.y()/self.height()))
                
            else :
                self.__isDrag = False
        
        self.__mainWindow.updateViews()
    
    def wheelEvent(self,event):
        
        dy = float(event.angleDelta().y())

        if self.__mainWindow.selectObjects:
            if self.__mode == 3:
                for obj in self.__mainWindow.selectObjects:
                    if type(obj) is data.WallPlane:
                        obj.moveByNormal(dy/3000)


        self.__mainWindow.updateViews()

    def keyPressEvent(self, event):

        if(event.key() == Qt.Key_Q):
            self.modeSwitch(1)
        elif(event.key() == Qt.Key_W):
            self.modeSwitch(2)
        elif(event.key() == Qt.Key_E):
            self.modeSwitch(3)

        if(event.key() == Qt.Key_S):
            self.__mainScene.label.genManhLayoutWalls()
            self.__mainWindow.updateListView()
                                    
        elif(event.key() == Qt.Key_X):
            self.__mainScene.label.cleanLayout()
            self.__mainWindow.updateListView()

        elif(event.key() == Qt.Key_D):
            self.__mainScene.label.delLayoutWalls(self.__mainWindow.selectObjects)
            self.__mainWindow.updateListView()

        elif(event.key() == Qt.Key_M):
            self.__mainScene.label.mergeLayoutWalls(self.__mainWindow.selectObjects)
            self.__mainWindow.updateListView()


        if (event.key() == Qt.Key_1):
            self.isLayoutWallEnable = not self.isLayoutWallEnable

        elif (event.key() == Qt.Key_2):
            self.isLayoutPointEnable = not self.isLayoutPointEnable

        self.__mainWindow.updateViews()
        
    def keyReleaseEvent(self, event):
        pass

    def enterEvent(self, event):
        self.setFocus(True)
    
    def leaveEvent(self, event):
        pass


    def setMainWindow(self, mainWindow):
        self.__mainWindow = mainWindow