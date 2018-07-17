
import sys
import numpy as np
from PIL import Image as Image
import math

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from OpenGL.GL import *
from OpenGL.GLU import *

import data
import utils
import configs

class MonoView(QOpenGLWidget):

    def __init__(self, parent=None):
        super(MonoView, self).__init__(parent)

        self.__isAvailable = False
        self.__mainWindow = None
        self.__mainScene = None

        ### Rendering
        self.__panoTexture = 0

        ### trackball
        self.__camRot = [0.0, 0.0, 0.0]
        self.__lastPos = QPoint()
        self.__fov = configs.Params.monoViewFov
        self.__isDrag = False

    #####
    #Comstum Method
    #####
    def initByScene(self, scene):
        self.__mainScene = scene
        self.__panoTexture = self.genTextureByImage(scene.getPanoColorImage())

        self.__isAvailable = True
        self.update()
        
    
    def createGeoPoint(self, screenPos):
        
        camPos = (-self.__camRot[0], -self.__camRot[1])
        screenSize = (self.width(), self.height())

        coords = utils.cameraPoint2pano(camPos, screenPos,
                                                        screenSize, self.__fov)
        geoPoint = data.GeoPoint(self.__mainScene, coords)

        return geoPoint
    
    def drawWallPlane(self, wallPlane):
        
        glBegin(GL_QUADS)
        rgb = wallPlane.color
        glColor4f(rgb[0], rgb[1], rgb[2], 0.2)
        mesh = wallPlane.mesh
        for vert in mesh:
            glVertex3f(vert[0], vert[1], vert[2])
        glEnd()

        glLineWidth(3)
        glBegin(GL_LINE_STRIP)
        #glLineWidth(3)
        glColor3f(0, 0, 1)
        for vert in mesh:
            glVertex3f(vert[0], vert[1], vert[2])
        glEnd()


    #####
    #Override
    #####
    def initializeGL(self):
        print("initializeGL")

        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClearDepth(1.0)

        glShadeModel(GL_SMOOTH)
        #glEnable(GL_CULL_FACE)
        glEnable(GL_DEPTH_TEST)

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glEnable(GL_LINE_SMOOTH)

        #glPolygonMode( GL_FRONT_AND_BACK, GL_LINE )

    def paintGL(self):

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(0.0, 0.0, 0.0,  0.0, 0.0, -1.0,  0.0, 1.0, 0.0)

        glPushMatrix()
        
        glRotated(90, 1.0, 0.0, 0.0)
        glRotated(-self.__camRot[1], 1.0, 0.0, 0.0)
        glRotated(self.__camRot[0], 0.0, 0.0, 1.0)
        #glTranslated(0.0, 0.0, -15.0)
        
        glColor3f(1.0, 1.0, 1.0)
        if self.__isAvailable:

            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.__panoTexture)

            sphere = gluNewQuadric()
            gluQuadricTexture(sphere, True)
            gluSphere(sphere, 20, 64, 32)

            glDisable(GL_TEXTURE_2D)

            glPushMatrix()
            glRotated(-90, 1.0, 0.0, 0.0)
            layoutWalls = self.__mainScene.label.getLayoutWalls()
            for wall in layoutWalls:
                self.drawWallPlane(wall)
            glPopMatrix()

        glPopMatrix()
    
    def resizeGL(self, width, height):
        print("resizeGL")

        side = min(width, height)
        glViewport((width - side) // 2, (height - side) // 2, side, side)
        
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        
        gluPerspective(self.__fov[1], width/height, 0.1, 1000)
        self.__fov = (self.__fov[1] *  width/height, self.__fov[1])

        #glOrtho(-1.0, 1.0, -1.0, 1.0, -10.0, 10.0)
        #glFrustum(-1.0, 1.0, -1.0, 1.0, 5.0, 40.0)

    def mousePressEvent(self, event):
        self.__lastPos = event.pos()
    
    def mouseMoveEvent(self, event):
        #print("point : {0} {1}".format(event.pos().x(), event.pos().y()))

        self.__isDrag = True

        dx = event.x() - self.__lastPos.x()
        dy = event.y() - self.__lastPos.y()

        if event.buttons() & Qt.LeftButton:
            self.__camRot[0] += 0.5 * dx
            self.__camRot[1] += 0.5 * dy

        xf, yf = utils.cameraPoseFix(self.__camRot[0], self.__camRot[1])
        self.__camRot[0] = xf
        self.__camRot[1] = yf

        self.__lastPos = event.pos()
        self.__mainWindow.updateViews()

    def mouseReleaseEvent(self, event):
        #print("Point : {0} {1}".format(event.pos().x(), event.pos().y()))
        screenPos = (event.pos().x(),event.pos().y())
        
        if not self.__isDrag:

            if self.__isAvailable:
                geoPoint = self.createGeoPoint(screenPos)
                self.__mainScene.label.addLayoutPoint(geoPoint)
        
        else :
            self.__isDrag = False
        
        self.__mainWindow.updateViews()
    
    def keyPressEvent(self, event):
        pass
    
    def keyReleaseEvent(self, event):
        pass
    
    def enterEvent(self, event):
        self.setFocus(True)
    
    def leaveEvent(self, event):
        pass


    def setMainWindow(self, mainWindow):
        self.__mainWindow = mainWindow

    def genTextureByImage(self, image):

        img_data = np.array(list(image.getdata()), np.int8)
        
        textID = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, textID)

        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.size[0], image.size[1], 0, 
                    GL_RGB, GL_UNSIGNED_BYTE, img_data)
        
        return textID
    