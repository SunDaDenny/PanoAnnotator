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

        def genItem(obj, name):
            item = QTreeWidgetItem(self)
            item.setText(0, name)
            item.setText(1, str(obj.id).zfill(5))
            self.itemLinks[obj] = item

        floor = self.__scene.label.getLayoutFloor()
        genItem(floor, 'Floor')
        ceiling = self.__scene.label.getLayoutCeiling()
        genItem(ceiling, 'Ceiling')

        walls = self.__scene.label.getLayoutWalls()
        for wall in walls:
            genItem(wall, 'Wall')

        obj2ds = self.__scene.label.getLayoutObject2d()
        for obj2d in obj2ds:
            genItem(obj2d, 'Object')
        
    def getSelectObjects(self, objType):
        
        objs = []
        for obj, item in self.itemLinks.items():
            if item in self.selectedItems():
                if obj in self.__scene.selectObjs:
                    if type(obj) == objType:
                        objs.append(obj)
        return objs

    def onTreeClicked(self, QModelIndex):

        for obj, item in self.itemLinks.items():
            if item in self.selectedItems():
                if obj not in self.__scene.selectObjs:
                    self.__scene.selectObjs.append(obj)
            else:
                if obj in self.__scene.selectObjs:
                    self.__scene.selectObjs.remove(obj)
    
    def keyPressEvent(self, event):

        walls = self.getSelectObjects(data.WallPlane)
        obj2ds = self.getSelectObjects(data.Object2D)

        if(event.key() == Qt.Key_D):
            if walls or obj2ds:
                self.__scene.label.delLayoutObject2ds(obj2ds)
                self.__scene.label.delLayoutWalls(walls)
                self.refreshList()

        if(event.key() == Qt.Key_M):
            self.__scene.label.mergeLayoutWalls(walls)
            self.refreshList()
        
    
    def enterEvent(self, event):
        self.setFocus(True)
    
    def leaveEvent(self, event):
        pass

    def setMainWindow(self, mainWindow):
        self.__mainWindow = mainWindow

        
        