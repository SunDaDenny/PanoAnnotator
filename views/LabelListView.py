import data
import utils
import configs

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QAbstractItemView

class LabelListView(QTreeWidget):

    def __init__(self, parent=None):
        super(LabelListView, self).__init__(parent)

        self.__isAvailable = False
        self.__mainWindow = None
        self.__scene = None

        self.setColumnCount(2)
        self.setHeaderLabels(['Name', 'ID'])

        self.itemLinks = {}

        self.clicked.connect(self.onTreeClicked)

        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        
    def initByScene(self, scene):
        
        self.__scene = scene
        
        self.refreshList()

        self.__isAvailable = True
        self.update()

    def refreshList(self):

        self.clear()
        self.itemLinks = {}

        points = self.__scene.label.getLayoutPoints()
        for point in points:
            item = QTreeWidgetItem(self)
            item.setText(0, 'GeoPoint')
            item.setText(1, str(point.id).zfill(5))
            self.itemLinks[point] = item

        walls = self.__scene.label.getLayoutWalls()
        for wall in walls:
            item = QTreeWidgetItem(self)
            item.setText(0, 'WallPlane')
            item.setText(1, str(wall.id).zfill(5))
            self.itemLinks[wall] = item
    
    def getSelectObjects(self):
        
        gps = []
        walls = []
        for obj, item in self.itemLinks.items():
            if item in self.selectedItems():
                if obj in self.__scene.selectObjs:
                    if type(obj) == data.GeoPoint:
                        gps.append(obj)
                    elif type(obj) == data.WallPlane:
                        walls.append(obj)
        return gps, walls

    def onTreeClicked(self, QModelIndex):

        for obj, item in self.itemLinks.items():
            if item in self.selectedItems():
                if obj not in self.__scene.selectObjs:
                    self.__scene.selectObjs.append(obj)
            else:
                if obj in self.__scene.selectObjs:
                    self.__scene.selectObjs.remove(obj)
    
    def keyPressEvent(self, event):

        gps, walls = self.getSelectObjects()
        if(event.key() == Qt.Key_D):
            for point in gps:
                self.__scene.label.delLayoutPoint(point)
            self.__scene.label.delLayoutWalls(walls)
            self.refreshList()

        if(event.key() == Qt.Key_M):
            self.__scene.label.mergeLayoutWalls(walls)
            self.refreshList()
        
        if(event.key() == Qt.Key_C):
            self.__scene.label.genConvexPoints(walls)
            self.refreshList()

    
    def enterEvent(self, event):
        self.setFocus(True)
    
    def leaveEvent(self, event):
        pass

    def setMainWindow(self, mainWindow):
        self.__mainWindow = mainWindow

        
        