import data
import utils

from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QPixmap, QPainter, QPen

class PanoView(QLabel):

    def __init__(self, parent=None):
        super(PanoView, self).__init__(parent)

        self.__isAvailable = False
        self.__mainWindow = None
        self.__scene = None

        self.__panoPixmap = QPixmap()
        self.__panoLinesPixmap = QPixmap()
        self.__panoOmapPixmap = QPixmap()

        self.__layoutEdgeMapPixmap = QPixmap()

        self.__mode = 0 #0: select mode 1: add point
        self.__keyPress = 0 #0:none 1:crtl 2:shift 3:alt
        self.__lastPos = QPoint()

        self.isLayoutLineEnable = True
        self.isLayoutPointEnable = False
        self.isLayoutFinalWallEnable = False
        self.isLayoutEdgeMapEnable = False
        self.isLayoutNormalMapEnable = False
        
        self.isPanoLinesEnable = False
        self.isPanoOmapEnable = False

    #####
    #Comstum Method
    #####
    def initByScene(self, scene):

        self.__scene = scene
        self.__panoPixmap = self.__scene.getPanoColorPixmap()
        self.__panoLinesPixmap = self.__scene.getPanoLinesPixmap()
        self.__panoOmapPixmap = self.__scene.getPanoOmapPixmap()

        self.__layoutEdgeMapPixmap = self.__scene.getLayoutEdgeMapPixmap()
        self.__layoutNormalMapPixmap = self.__scene.getLayoutNormalMapPixmap()

        self.__isAvailable = True

    def createGeoPoint(self, sceenPos):
        
        coords = utils.pos2coords(sceenPos, 
                                            (self.width(), self.height()))
        geoPoint = data.GeoPoint(self.__scene, coords)

        return geoPoint
    

    def selectByCoords(self, coords):
        
        vec =  utils.coords2xyz(coords, 1)

        def choose(self, obj, point):
            select = self.__scene.selectObjs
            if obj in select:
                select.remove(obj)
            else:
                if self.__keyPress == 0:
                    select[:] = []
                    select.append(obj)
                elif self.__keyPress == 1:
                    select.append(obj)
                elif self.__keyPress == 2:
                    select.append(obj)
                    
                    flag = False
                    for wall in self.__scene.label.getLayoutWalls():
                        if wall in select:
                            flag = not flag
                        if flag and not wall in select :
                            select.append(wall)

                elif self.__keyPress == 3:
                    if point:
                        self.__scene.label.genSplitPoints(obj, point)

        for wall in self.__scene.label.getLayoutWalls():
            isHit, point = wall.checkRayHit(vec)
            if isHit:
                choose(self, wall, point)
                return

        floor = self.__scene.label.getLayoutFloor()
        ceiling = self.__scene.label.getLayoutCeiling()
        choose(self, floor, None) if vec[1] <= 0 else choose(self, ceiling, None)

    def drawEdges(self, qp, obj):

        size = (self.width(), self.height())
        for edge in obj.edges:
            for i in range(len(edge.coords)-1):
                isCross, l, r = utils.pointsCrossPano(edge.sample[i],edge.sample[i+1])
                if not isCross:
                    pos1 = utils.coords2pos(edge.coords[i], size)
                    pos2 = utils.coords2pos(edge.coords[i+1], size)
                    qp.drawLine(pos1[0], pos1[1], pos2[0], pos2[1])
                else:
                    lpos = utils.coords2pos(utils.xyz2coords(l), size)
                    rpos = utils.coords2pos(utils.xyz2coords(r), size)
                    ch = int((lpos[1] + rpos[1])/2)
                    qp.drawLine(lpos[0], lpos[1], 0, ch)
                    qp.drawLine(rpos[0], rpos[1], size[0], ch)

    #####
    #Override
    #####
    def paintEvent(self, event):
        
        if self.__isAvailable:
            qp = QPainter()

            qp.begin(self)
            qp.drawPixmap(0, 0, self.width(), self.height(), self.__panoPixmap)
            
            qp.setOpacity(1.0)
            if self.__panoLinesPixmap and self.isPanoLinesEnable:
                qp.drawPixmap(0, 0, self.width(), self.height(), self.__panoLinesPixmap)
            qp.setOpacity(0.75)
            if self.isLayoutEdgeMapEnable:
                self.__layoutEdgeMapPixmap = self.__scene.getLayoutEdgeMapPixmap()
                if self.__layoutEdgeMapPixmap:
                    qp.drawPixmap(0, 0, self.width(), self.height(), self.__layoutEdgeMapPixmap)

            qp.setOpacity(1.0)
            if self.__panoOmapPixmap and self.isPanoOmapEnable:  
                qp.drawPixmap(0, 0, self.width(), self.height(), self.__panoOmapPixmap)
            qp.setOpacity(0.5)
            if self.isLayoutNormalMapEnable:
                self.__layoutNormalMapPixmap = self.__scene.getLayoutNormalMapPixmap()
                if self.__layoutNormalMapPixmap:
                    qp.drawPixmap(0, 0, self.width(), self.height(), self.__layoutNormalMapPixmap)
            
            qp.setOpacity(1.0)

            if self.isLayoutPointEnable:

                for point in self.__scene.label.getLayoutPoints():

                    if point in self.__scene.selectObjs:
                        qp.setPen(QPen(Qt.yellow, 2, Qt.SolidLine))
                    else:
                        qp.setPen(QPen(Qt.red, 2, Qt.SolidLine))

                    pos = utils.coords2pos(point.coords, 
                                                    (self.width(), self.height()))
                    qp.drawEllipse(QPoint(pos[0], pos[1]), 5, 5)
                    #qp.drawLine(pos[0], 0, pos[0], self.height())
            
            if self.isLayoutLineEnable:

                #draw all obj first
                if self.isPanoLinesEnable:
                    qp.setPen(QPen(Qt.white, 1, Qt.SolidLine))
                elif self.isPanoOmapEnable:
                    qp.setPen(QPen(Qt.white, 2, Qt.SolidLine))
                else:
                    qp.setPen(QPen(Qt.blue, 2, Qt.SolidLine))
                for wall in  self.__scene.label.getLayoutWalls():
                    self.drawEdges(qp, wall)

                floor = self.__scene.label.getLayoutFloor()
                ceiling = self.__scene.label.getLayoutCeiling()
                if floor is not None:
                    self.drawEdges(qp, floor)
                if ceiling is not None:
                    self.drawEdges(qp, ceiling) 

                #darw selected obj again
                qp.setPen(QPen(Qt.yellow, 2, Qt.SolidLine))
                for obj in self.__scene.selectObjs:
                    if type(obj) == data.WallPlane or type(obj) == data.FloorPlane:
                        self.drawEdges(qp, obj)


            ###TEST
            '''
            qp.setPen(QPen(Qt.red, 1, Qt.SolidLine))
            size = (self.width(), self.height())
            for wall in  self.__scene.label.getLayoutWalls():     
                poslt = utils.coords2pos(wall.bbox2d[0], size)
                posrb = utils.coords2pos(wall.bbox2d[1], size)
                qp.drawRect(poslt[0], poslt[1],
                            posrb[0]-poslt[0], posrb[1]-poslt[1])  
            '''

            qp.setPen(QPen(Qt.green, 4, Qt.SolidLine))
            #qp.drawText(10, 10, "Mode : {0}".format(self.__mode))
            qp.drawText(10, 10, "FPS : {0:.2f}".format(utils.getFPS()))

            qp.end()

        self.__mainWindow.updateViews()

    def mousePressEvent(self, event):
        self.__lastPos = event.pos()

    def mouseMoveEvent(self, event):

        dx = event.x() - self.__lastPos.x()
        dy = event.y() - self.__lastPos.y()

        self.__mainWindow.updateViews()

    def mouseReleaseEvent(self, event):

        screenPos = (event.pos().x(),event.pos().y())
        if self.__isAvailable:
   
            if event.button() == Qt.LeftButton:
                if self.__mode == 0:
                    self.selectByCoords((event.x()/self.width(),
                                        event.y()/self.height()))
                    self.__mainWindow.updateListView()
                                        
                elif self.__mode == 1:
                    geoPoint = self.createGeoPoint(screenPos)
                    self.__scene.label.addLayoutPoint(geoPoint)
                    self.__mainWindow.updateListView()

            elif event.button() == Qt.RightButton:
                if self.__mode == 1:
                    self.__scene.label.delLastLayoutPoints()
                    self.__mainWindow.updateListView()
                
        self.__mainWindow.updateViews()
    
    def wheelEvent(self,event):
        
        dy = float(event.angleDelta().y())

        for wall in self.__scene.getSelectObjs('WallPlane'):
            if self.__keyPress == 2:
                self.__scene.label.moveWallByPred(wall, dy/3000)
            else:
                self.__scene.label.moveWallByNormal(wall, dy/3000)

        for floorplane in self.__scene.getSelectObjs('FloorPlane'):
            #if self.__keyPress == 2:
            #    self.__scene.label.moveObjByPred(floorplane, dy/3000)
            if not floorplane.isCeiling():
                self.__scene.label.moveFloor(-float(dy)/1000)
            else:
                self.__scene.label.moveCeiling(float(dy)/1000)

        self.__mainWindow.updateViews()

    def keyPressEvent(self, event):

        if(event.key() == Qt.Key_Control):
            self.__keyPress = 1
        elif(event.key() == Qt.Key_Shift):
            self.__keyPress = 2
        elif(event.key() == Qt.Key_Alt):
            self.__keyPress = 3


        if(event.key() == Qt.Key_Space):
            self.__scene.label.genManhLayoutWalls()

        elif(event.key() == Qt.Key_I):
            self.__scene.label.calcInitLayout()
                                
        elif(event.key() == Qt.Key_C):
            self.__scene.label.cleanLayout()

        elif(event.key() == Qt.Key_D):
            walls = self.__scene.getSelectObjs('WallPlane')
            self.__scene.label.delLayoutWalls(walls)

        elif(event.key() == Qt.Key_M):
            walls = self.__scene.getSelectObjs('WallPlane')
            self.__scene.label.mergeLayoutWalls(walls)

        elif(event.key() == Qt.Key_G):
            walls = self.__scene.getSelectObjs('WallPlane')
            self.__scene.label.genConvexPoints(walls)
        
        self.__mainWindow.updateListView()


        if (event.key() == Qt.Key_1):
            self.isLayoutLineEnable = not self.isLayoutLineEnable
        elif (event.key() == Qt.Key_2):
            self.isLayoutPointEnable = not self.isLayoutPointEnable
        elif (event.key() == Qt.Key_3):
            self.isPanoLinesEnable = not self.isPanoLinesEnable
        elif (event.key() == Qt.Key_4):
            self.isLayoutEdgeMapEnable = not self.isLayoutEdgeMapEnable
        elif (event.key() == Qt.Key_5):
            self.isPanoOmapEnable = not self.isPanoOmapEnable
        elif (event.key() == Qt.Key_6):
            self.isLayoutNormalMapEnable = not self.isLayoutNormalMapEnable

        self.__mainWindow.updateViews()
        
    def keyReleaseEvent(self, event):
        self.__keyPress = 0

    def enterEvent(self, event):
        self.setFocus(True)
    
    def leaveEvent(self, event):
        pass


    def setMainWindow(self, mainWindow):
        self.__mainWindow = mainWindow