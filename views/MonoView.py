import numpy as np

import data
import utils
import configs.Params as pm

from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtGui import QPixmap

from OpenGL.GL import *
from OpenGL.GLU import *

class MonoView(QOpenGLWidget):

    def __init__(self, parent=None):
        super(MonoView, self).__init__(parent)

        self.__isAvailable = False
        self.__mainWindow = None
        self.__scene = None

        ### Rendering
        self.__panoTexture = 0

        ### trackball
        self.__camRot = [0.0, 0.0, 0.0]
        self.__keyPress = pm.keyDict['none']
        self.__lastPos = QPoint()
        self.__fov = pm.monoViewFov

        self.__hitInfo = [] #(obj, hit point)
        self.__hitSelect = 0

    #####
    #Comstum Method
    #####
    def initByScene(self, scene):
        self.__scene = scene

        image = scene.getPanoColorImage()
        self.__panoTexture = self.genTextureByImage(image)

        self.__isAvailable = True
        self.update()

    '''    
    def createGeoPoint(self, screenPos):
        
        camPos = (-self.__camRot[0], -self.__camRot[1])
        screenSize = (self.width(), self.height())

        coords = utils.cameraPoint2pano(camPos, screenPos,
                                        screenSize, self.__fov)
        geoPoint = data.GeoPoint(self.__scene, coords)

        return geoPoint
    '''

    def selectByCoords(self, coords):
        
        vec =  utils.coords2xyz(coords, 1)

        self.__hitInfo = []
        for wall in self.__scene.label.getLayoutWalls():
            isHit, point = wall.checkRayHit(vec)
            if isHit:
                self.__hitInfo.append((wall, point))

        if self.__hitInfo:
            self.__hitInfo.sort(key=lambda x:abs(x[0].planeEquation[3]), reverse=True)
            self.selectObject(self.__hitInfo[0][0], self.__hitInfo[0][1])
            self.__hitSelect = 0
        elif vec[1]<=0:
            self.selectObject(self.__scene.label.getLayoutFloor(), None)
        else:
            self.selectObject(self.__scene.label.getLayoutCeiling(), None)

    def selectByVector(self, vec):

        self.__hitInfo = []
        for wall in self.__scene.label.getLayoutWalls():
            isHit, point = wall.checkRayHit(vec)
            if isHit:
                self.__hitInfo.append((wall, point))

        if self.__hitInfo:
            self.__hitInfo.sort(key=lambda x:abs(x[0].planeEquation[3]), reverse=True)
            self.selectObject(self.__hitInfo[0][0], self.__hitInfo[0][1])
            self.__hitSelect = 0
        elif vec[1]<=0:
            self.selectObject(self.__scene.label.getLayoutFloor(), None)
        else:
            self.selectObject(self.__scene.label.getLayoutCeiling(), None)

    def selectObject(self, obj, point):

        select = self.__scene.selectObjs
        if obj in select:
            select.remove(obj)
        elif self.__keyPress == pm.keyDict['none']:
            select[:] = []
            select.append(obj)
        elif self.__keyPress == pm.keyDict['ctrl']:
            select.append(obj)
        elif self.__keyPress == pm.keyDict['shift']:
            self.multiSelect(obj)

        elif self.__keyPress == pm.keyDict['alt'] and point:
            self.__scene.label.genSplitPoints(obj, point)

    def multiSelect(self, obj):

        select = self.__scene.selectObjs
        walls = self.__scene.label.getLayoutWalls()
        selectWalls = self.__scene.getSelectObjs('WallPlane')

        if selectWalls:
            owall = selectWalls[0]
            idxl = min(walls.index(owall),walls.index(obj))
            idxu = max(walls.index(owall),walls.index(obj))

            if idxu - idxl < len(walls)/2:
                idxList = list(range(idxl, idxu+1))
            else:
                listl = list(range(0, idxl+1))
                listu = list(range(idxu, len(walls)))
                idxList = listl + listu
            for i in idxList:
                if walls[i] not in selectWalls:
                    select.append(walls[i])
        else:
            select.append(obj)

    def drawEdges(self, obj):
        
        glLineWidth(3)
        glBegin(GL_LINE_STRIP)
        for p in obj.corners:
            glVertex3f(p.xyz[0], p.xyz[1], p.xyz[2])
        first = obj.corners[0]
        glVertex3f(first.xyz[0], first.xyz[1], first.xyz[2])
        glEnd()
        
    def drawWallPlane(self, wall):
        
        '''
        glBegin(GL_QUADS)
        rgb = wallPlane.color
        glColor4f(rgb[0], rgb[1], rgb[2], 0.5)
        for p in wallPlane.corners:
            glVertex3f(p.xyz[0], p.xyz[1], p.xyz[2])
        glEnd()
        '''
        
        glLineWidth(3)
        glBegin(GL_LINE_STRIP)
        for p in wall.corners:
            glVertex3f(p.xyz[0], p.xyz[1], p.xyz[2])
        glEnd()


    #####
    #Override
    #####
    def initializeGL(self):

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
        glRotated(self.__camRot[1], 1.0, 0.0, 0.0)
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

            glColor3f(1 ,1 ,0)
            for obj in self.__scene.selectObjs:
                if type(obj) == data.WallPlane or type(obj) == data.FloorPlane:
                    self.drawEdges(obj)
            
            glColor3f(0 ,0 ,1)
            walls = self.__scene.label.getLayoutWalls()
            for wall in walls:
                self.drawEdges(wall)

            floor = self.__scene.label.getLayoutFloor()
            ceiling = self.__scene.label.getLayoutCeiling()
            if floor is not None:
                self.drawEdges(floor)
            if ceiling is not None:
                self.drawEdges(ceiling)

            glPopMatrix()

        glPopMatrix()
    
    def resizeGL(self, width, height):

        side = min(width, height)
        glViewport((width - side) // 2, (height - side) // 2, side, side)
        
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        
        gluPerspective(self.__fov[1], width/height, 0.1, 1000)
        self.__fov = (self.__fov[1] * width/height, self.__fov[1])
        #print(self.__fov)

        #glOrtho(-1.0, 1.0, -1.0, 1.0, -10.0, 10.0)
        #glFrustum(-1.0, 1.0, -1.0, 1.0, 5.0, 40.0)

    ###auto rotation
    def moveCamera(self, coords):

        self.__camRot[0] = -(coords[0] - 0.5) * 360
        self.__camRot[1] = (coords[1] - 0.5) * 180

    def mousePressEvent(self, event):
        self.__lastPos = event.pos()

        #camPos = (-self.__camRot[0], -self.__camRot[1])
        #screenPos = (event.pos().x(),event.pos().y())
        #screenSize = (self.width(), self.height())
        #coords = utils.cameraPoint2pano(camPos, screenPos,
        #                                screenSize, self.__fov)
        
        camPos = (self.__camRot[0] + 180, self.__camRot[1])
        coords = (event.x()/self.width(), event.y()/self.height())
        vec = utils.cameraCoords2Vector(camPos, coords, self.__fov)

        if self.__isAvailable:
            if event.button() == Qt.LeftButton:
                #self.selectByCoords(coords)
                self.selectByVector(vec)
                self.__mainWindow.updateListView()
        
        self.__mainWindow.updateViews()

    def mouseMoveEvent(self, event):
        #print("point : {0} {1}".format(event.pos().x(), event.pos().y()))

        dx = event.x() - self.__lastPos.x()
        dy = event.y() - self.__lastPos.y()

        if event.buttons() & Qt.RightButton:
            self.__camRot[0] += 0.5 * dx
            self.__camRot[1] -= 0.5 * dy

        xf, yf = self.cameraPoseFix(self.__camRot)
        self.__camRot[0] = xf
        self.__camRot[1] = yf

        self.__lastPos = event.pos()
        self.__mainWindow.updateViews()

    def mouseReleaseEvent(self, event):
        self.__hitInfo = []

    def wheelEvent(self,event):

        dy = float(event.angleDelta().y())

        if self.__hitInfo:
            hitWall = self.__hitInfo[self.__hitSelect][0]
            if(hitWall in self.__scene.selectObjs):
                self.__scene.selectObjs.remove(hitWall)
                self.__hitSelect = (self.__hitSelect+1)%len(self.__hitInfo)
                self.__scene.selectObjs.append(self.__hitInfo[self.__hitSelect][0])

        for wall in self.__scene.getSelectObjs('WallPlane'):
            if self.__keyPress == pm.keyDict['shift']:
                self.__scene.label.moveWallByPred(wall, dy/3000)
            else:
                self.__scene.label.moveWallByNormal(wall, dy/3000)

        for floorplane in self.__scene.getSelectObjs('FloorPlane'):
            if not floorplane.isCeiling():
                self.__scene.label.moveFloor(-float(dy)/1000)
            else:
                self.__scene.label.moveCeiling(float(dy)/1000)

        self.__mainWindow.updateViews()       
    
    def keyPressEvent(self, event):
        
        if(event.key() == Qt.Key_Control):
            self.__keyPress = pm.keyDict['ctrl']
        elif(event.key() == Qt.Key_Shift):
            self.__keyPress = pm.keyDict['shift']
        elif(event.key() == Qt.Key_Alt):
            self.__keyPress = pm.keyDict['alt']

        if(event.key() == Qt.Key_D):
            walls = self.__scene.getSelectObjs('WallPlane')
            self.__scene.label.delLayoutWalls(walls)
        elif(event.key() == Qt.Key_M):
            walls = self.__scene.getSelectObjs('WallPlane')
            self.__scene.label.mergeLayoutWalls(walls)

    def keyReleaseEvent(self, event):
        self.__keyPress = pm.keyDict['none']
    
    def enterEvent(self, event):
        self.setFocus(True)
    
    def leaveEvent(self, event):
        pass

    def setMainWindow(self, mainWindow):
        self.__mainWindow = mainWindow

    def cameraPoseFix(self, pose):
        ### x : -180 ~ 180
        ### y : -90 ~ 90
        x = pose[0]
        y = pose[1]

        if x > 180:
            x -= 360
        elif x < -180:
            x += 360
        if y > 90:
            y = 90
        elif y < -90:
            y = -90
        return (x, y)

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
    