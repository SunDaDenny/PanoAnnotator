import data
import utils
import configs.Params as pm

from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor

class PanoView(QLabel):

    def __init__(self, parent=None):
        super(PanoView, self).__init__(parent)

        self.__isAvailable = False
        self.__mainWindow = None
        self.__scene = None

        self.__keyPress = pm.keyDict['none']
        self.__dragPoints = []

        self.__hitWalls = [] #(wall, hit point)

        self.isLayoutLineEnable = True
        self.isLayoutObject2dEnable = True
        self.isLayoutPointEnable = False
        
        self.isPanoLinesEnable = False
        self.isPanoOmapEnable = False

    #####
    #Comstum Method
    #####
    def initByScene(self, scene):

        self.__scene = scene
        self.__isAvailable = True
    
    def selectByCoords(self, coords):
        
        vec =  utils.coords2xyz(coords, 1)

        #select object2d first
        for obj2d in self.__scene.label.getLayoutObject2d():
            isHit, point = obj2d.checkRayHit(vec)
            if isHit:
                self.selectObject(obj2d, point)
                return

        #select walls and save all hit wall into hitinfo
        self.__hitWalls = []
        for wall in self.__scene.label.getLayoutWalls():
            isHit, point = wall.checkRayHit(vec)
            if isHit:
                self.__hitWalls.append((wall, point))
        if self.__hitWalls:
            wall, point = self.__hitWalls[0]
            self.selectObject(wall, point)
            return

        #select floor and ceiling
        if vec[1]<=0:
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
            if type(obj) is data.WallPlane:
                self.__scene.label.genSplitPoints(obj, point)

    def multiSelect(self, obj):

        if type(obj) is not data.WallPlane:
            return
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

    def selectNextHit(self):

        hits = self.__hitWalls
        select = self.__scene.selectObjs
        if not hits:
            return
        obj, point = hits[0]
        if obj in select:
            select.remove(obj)
            hits.insert(0, hits.pop())
            select.append(hits[0][0])

    #####
    #Override
    #####
    def paintEvent(self, event):

        size = (self.width(), self.height())

        def drawEdges(qp, obj):
            for edge in obj.edges:
                for i in range(len(edge.coords)-1):
                    isCross, l, r = utils.pointsCrossPano(edge.sample[i],
                                                          edge.sample[i+1])
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
        
        if not self.__isAvailable:
            return

        qp = QPainter()
        qp.begin(self)
        panoPixmap = self.__scene.getPanoColorPixmap()
        qp.drawPixmap(0, 0, size[0], size[1], panoPixmap)
        
        qp.setOpacity(1.0)
        linesPixmap = self.__scene.getPanoLinesPixmap()
        if linesPixmap and self.isPanoLinesEnable:
            qp.drawPixmap(0, 0, size[0], size[1], linesPixmap)

        qp.setOpacity(1.0)
        OmapPixmap = self.__scene.getPanoOmapPixmap() 
        if OmapPixmap and self.isPanoOmapEnable:  
            qp.drawPixmap(0, 0, size[0], size[1], OmapPixmap)

        qp.setPen(QPen(Qt.red, 2, Qt.SolidLine))        
        if self.__dragPoints:
            pos = utils.xyz2pos(self.__dragPoints[0], size)
            qp.drawEllipse(QPoint(pos[0], pos[1]), 5, 5)
            if len(self.__dragPoints)==2:
                pos2 = utils.xyz2pos(self.__dragPoints[1], size)
                qp.drawEllipse(QPoint(pos2[0], pos2[1]), 5, 5)
                qp.drawLine(pos[0], pos[1], pos2[0], pos2[1])

        if self.isLayoutPointEnable:

            for point in self.__scene.label.getLayoutPoints():

                if point in self.__scene.selectObjs:
                    qp.setPen(QPen(Qt.yellow, 2, Qt.SolidLine))
                else:
                    qp.setPen(QPen(Qt.red, 2, Qt.SolidLine))

                pos = utils.coords2pos(point.coords, size)
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
                drawEdges(qp, wall)

            floor = self.__scene.label.getLayoutFloor()
            ceiling = self.__scene.label.getLayoutCeiling()
            if floor is not None:
                drawEdges(qp, floor)
            if ceiling is not None:
                drawEdges(qp, ceiling) 

            #darw selected obj again
            qp.setPen(QPen(Qt.yellow, 2, Qt.SolidLine))
            for obj in self.__scene.getSelectObjs('WallPlane'):
                drawEdges(qp, obj)
            for obj in self.__scene.getSelectObjs('FloorPlane'):
                drawEdges(qp, obj)

        if self.isLayoutObject2dEnable:
            
            for obj in self.__scene.label.getLayoutObject2d():
                qp.setPen(QPen(QColor(0,255,255), 2, Qt.SolidLine))
                drawEdges(qp, obj)
            for obj in self.__scene.getSelectObjs('Object2D'):
                qp.setPen(QPen(Qt.yellow, 2, Qt.SolidLine))
                drawEdges(qp, obj)
            
        ###TEST
        '''
        def drawBbox(obj):
            size = (self.width(), self.height())
            poslt = utils.coords2pos(obj.bbox2d[0], size)
            posrb = utils.coords2pos(obj.bbox2d[1], size)
            qp.drawRect(poslt[0], poslt[1],
                        posrb[0]-poslt[0], posrb[1]-poslt[1])
        qp.setPen(QPen(Qt.red, 1, Qt.SolidLine))
        drawBbox(self.__scene.label.getLayoutFloor())
        drawBbox(self.__scene.label.getLayoutCeiling())
        for wall in  self.__scene.label.getLayoutWalls():     
            drawBbox(wall) 
        '''

        qp.setPen(QPen(Qt.green, 4, Qt.SolidLine))
        qp.drawText(10, 10, "FPS : {0:.2f}".format(utils.getFPS()))

        qp.end()

        self.__mainWindow.updateViews()

    def mousePressEvent(self, event):
        
        if not self.__isAvailable:
            return
        coords = (event.x()/self.width(),event.y()/self.height())

        if event.button() == Qt.LeftButton:
            self.selectByCoords(coords)
            self.__mainWindow.updateListView()

        elif event.button() == Qt.RightButton:
            self.__mainWindow.moveMonoCamera(coords)
                
        self.__mainWindow.updateViews()

    def mouseMoveEvent(self, event):

        if not self.__isAvailable:
            return
        coords = (event.x()/self.width(),event.y()/self.height())
        vec =  utils.coords2xyz(coords, 1)
        if self.__keyPress == pm.keyDict['object'] and self.__hitWalls:
            wall, point1 = self.__hitWalls[0]
            isHit, point2 = wall.checkRayHit(vec)
            if isHit:
                self.__dragPoints = [point1, point2]

    def mouseReleaseEvent(self, event):

        if not self.__isAvailable:
            return

        if len(self.__dragPoints)==2:
            self.__scene.label.genObject2d(self.__dragPoints, 
                                            self.__hitWalls[0][0])
        self.__hitWalls = []
        self.__dragPoints = []

    def wheelEvent(self,event):
        
        dy = float(event.angleDelta().y())

        for wall in self.__scene.getSelectObjs('WallPlane'):
            if self.__keyPress == pm.keyDict['shift']:
                self.__scene.label.moveWallByPred(wall, dy)
            else:
                d = wall.planeEquation[3]
                move = dy / 5000 * -d + dy/3000
                self.__scene.label.moveWallByNormal(wall, move)

        for floorplane in self.__scene.getSelectObjs('FloorPlane'):
            if not floorplane.isCeiling():
                self.__scene.label.moveFloor(-float(dy)/3000)
            else:
                self.__scene.label.moveCeiling(float(dy)/3000)

        self.__mainWindow.updateViews()

    def keyPressEvent(self, event):

        if(event.key() == Qt.Key_Control):
            self.__keyPress = pm.keyDict['ctrl']
        elif(event.key() == Qt.Key_Shift):
            self.__keyPress = pm.keyDict['shift']
        elif(event.key() == Qt.Key_Alt):
            self.__keyPress = pm.keyDict['alt']
        elif(event.key() == Qt.Key_Z):
            self.__keyPress = pm.keyDict['object']

        elif(event.key() == Qt.Key_X):
            self.selectNextHit()

        elif(event.key() == Qt.Key_R):
            self.__scene.label.calcInitLayout()                        

        elif(event.key() == Qt.Key_D):
            obj2ds = self.__scene.getSelectObjs('Object2D')
            self.__scene.label.delLayoutObject2ds(obj2ds)
            walls = self.__scene.getSelectObjs('WallPlane')
            if walls:
                self.__scene.label.delLayoutWalls(walls)

        elif(event.key() == Qt.Key_Space):
            walls = self.__scene.getSelectObjs('WallPlane')
            self.__scene.label.mergeLayoutWalls(walls)

        self.__mainWindow.updateListView()

        if (event.key() == Qt.Key_1):
            self.isLayoutLineEnable = not self.isLayoutLineEnable
        elif (event.key() == Qt.Key_2):
            self.isLayoutPointEnable = not self.isLayoutPointEnable
        elif (event.key() == Qt.Key_3):
            isLayoutObject2dEnable = not self.isLayoutObject2dEnable
        elif (event.key() == Qt.Key_4):
            self.isPanoLinesEnable = not self.isPanoLinesEnable
        elif (event.key() == Qt.Key_5):
            self.isPanoOmapEnable = not self.isPanoOmapEnable

        self.__mainWindow.updateViews()
        
    def keyReleaseEvent(self, event):
        self.__keyPress = pm.keyDict['none']

    def enterEvent(self, event):
        self.setFocus(True)
    
    def leaveEvent(self, event):
        pass

    def setMainWindow(self, mainWindow):
        self.__mainWindow = mainWindow