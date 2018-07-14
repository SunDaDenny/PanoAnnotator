import sys
import numpy as np

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from OpenGL.GL import *
from OpenGL.GLU import *

import data
import configs.Params as pm
import utils

class ResultView(QOpenGLWidget):

    def __init__(self, parent=None):
        super(ResultView, self).__init__(parent)

        self.__isAvailable = False
        self.__mainWindow = None
        self.__mainScene = None

        ### trackball
        self.camRot = [0.0, 0.0, 0.0]
        self.camPos = [0.0, 0.0, 10.0]
        self.__lastPos = QPoint()

        self.isPointCloudEnable = False
        self.isLayoutWallEnable = True
        self.isLayoutPointEnable = True

        #self.geoTool = utils.GeometryTool()

    #####
    #Comstum Method
    #####
    def initByScene(self, scene):
        self.__mainScene = scene

        pointCloud = utils.createPointCloud(self.__mainScene.getPanoColorData(),
                                                self.__mainScene.getPanoDepthData() )
        self.__mainScene.setPanoPointCloud(pointCloud)

        self.__isAvailable = True
        self.update()

    def drawWallPlane(self, wallPlane):
        
        glBegin(GL_QUADS)

        rgb = wallPlane.color
        #glColor3f(rgb[0], rgb[1], rgb[2])
        glColor4f(rgb[0], rgb[1], rgb[2], 0.75)
        #glNormal3f(0.0, 0.0, 1.0)
        mesh = wallPlane.mesh
        for vert in mesh:
            glVertex3f(vert[0], vert[1], vert[2])
        glEnd()

    #####
    #Override
    #####
    def initializeGL(self):

        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClearDepth(1.0)

        glShadeModel(GL_SMOOTH)
        #glShadeModel(GL_FLAT)

        #glEnable(GL_CULL_FACE)
        glEnable(GL_DEPTH_TEST)

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        #glBlendFunc(GL_ONE, GL_ONE_MINUS_SRC_ALPHA)

        glEnable(GL_PROGRAM_POINT_SIZE)
    
    def paintGL(self):

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(self.camPos[0], self.camPos[1], self.camPos[2],
                  self.camPos[0], self.camPos[1], -1.0,  0.0, 1.0, 0.0)

        glPushMatrix()
        
        glRotated(self.camRot[0], 0.0, 1.0, 0.0)
        glRotated(self.camRot[1], 1.0, 0.0, 0.0)
        
        
        if self.__isAvailable:
            pointCloud = self.__mainScene.getPanoPointCloud()
            layoutPoints = self.__mainScene.label.getLayoutPoints()
            layoutWalls = self.__mainScene.label.getLayoutWalls()
            
            if self.isPointCloudEnable:
                glPointSize(3)
                glBegin(GL_POINTS)
                for point in pointCloud:
                    glColor3f( float(point[1][0])/255, float(point[1][1])/255, 
                            float(point[1][2])/255)
                    glVertex3f(point[0][0], point[0][1], point[0][2])
                glEnd()

            if self.isLayoutPointEnable:
                glPointSize(10)
                glBegin(GL_POINTS)          
                rgb = pm.resultPointColor[0]
                glColor3f(rgb[0], rgb[1], rgb[2])
                for point in layoutPoints:
                    glVertex3f(point.xyz[0], point.xyz[1], point.xyz[2])
                glEnd()

            if self.isLayoutWallEnable:
                for wall in layoutWalls:
                    self.drawWallPlane(wall)


        glPopMatrix()

    def resizeGL(sel, width, height):

        side = min(width, height)
        glViewport((width - side) // 2, (height - side) // 2, side, side)
        
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        gluPerspective(60, width/height, 1.0, 1000)
        
    def mousePressEvent(self, event):
        self.setFocus(True)
        self.__lastPos = event.pos()

        
    def mouseMoveEvent(self, event):
        #print("point : {0} {1}".format(event.pos().x(), event.pos().y()))
        dx = event.x() - self.__lastPos.x()
        dy = event.y() - self.__lastPos.y()

        if event.buttons() == Qt.LeftButton:
            self.camRot[0] += 0.5 * dx
            self.camRot[1] += 0.5 * dy

        elif event.buttons() == Qt.RightButton:
            self.camPos[0] -= 0.02 * dx
            self.camPos[1] += 0.02 * dy

        self.__lastPos = event.pos()
        self.update()
    
    def wheelEvent(self,event):
        
        numAngle = float(event.angleDelta().y()) / 120
        self.camPos[2] -= numAngle
        self.update()

    def keyPressEvent(self, event):

        if (event.key() == Qt.Key_1):
            self.isPointCloudEnable = not self.isPointCloudEnable

        if (event.key() == Qt.Key_2):
            self.isLayoutWallEnable = not self.isLayoutWallEnable

        if (event.key() == Qt.Key_3):
            self.isLayoutPointEnable = not self.isLayoutPointEnable

        
        self.update()

    def enterEvent(self, event):
        self.setFocus(True)
    
    def leaveEvent(self, event):
        pass


    def setMainWindow(self, mainWindow):
        self.__mainWindow = mainWindow
