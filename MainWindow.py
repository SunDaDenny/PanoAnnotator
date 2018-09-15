import sys
import os

import data
import configs.Params as pm
import views
import qdarkstyle
import estimator
import utils

from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QProgressDialog
from PyQt5.QtCore import QCoreApplication

class MainWindow(QMainWindow, views.MainWindowUi):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)

        self.actionOpenImage.triggered.connect(self.openImageFile)
        self.actionOpenJson.triggered.connect(self.openJsonFile)

        self.actionSaveFile.triggered.connect(self.saveSceneFile)

        self.mainScene = data.Scene(self)
        self.depthPred = estimator.DepthPred()

        self.panoView.setMainWindow(self)
        self.monoView.setMainWindow(self)
        self.resultView.setMainWindow(self)
        self.labelListView.setMainWindow(self)

    def openImageFile(self):
        filePath, ok = QFileDialog.getOpenFileName(self, "open", pm.fileDefaultOpenPath,
                                                  "Images (*.png *.jpg)")
        if ok:
            self.mainScene = self.createNewScene(filePath)
            self.mainScene.initLabel()
            self.initViewsByScene(self.mainScene)
        else:
            print('open file error')
        return ok

    def openJsonFile(self):
        filePath, ok = QFileDialog.getOpenFileName(self, "open", pm.fileDefaultOpenPath,
                                                  "Json (*.json)")
        if ok:
            imagePath = os.path.join(os.path.dirname(filePath), pm.colorFileDefaultName)
            self.mainScene = self.createNewScene(imagePath)
            self.mainScene.loadLabel(filePath)
            self.initViewsByScene(self.mainScene)
        else:
            print('open file error')
        return ok
    
    def saveSceneFile(self):
        
        curPath = self.mainScene.getCurrentPath()
        savePath = curPath + pm.labelFileDefaultName
        #utils.saveSceneAsMaps(savePath, self.mainScene)
        utils.saveSceneAsJson(savePath, self.mainScene)

    def createNewScene(self, filePath):
        scene = data.Scene(self)
        scene.initScene(filePath, self.depthPred)

        return scene

    def initViewsByScene(self, scene):

        self.panoView.initByScene(scene)
        self.monoView.initByScene(scene)
        self.resultView.initByScene(scene)
        self.labelListView.initByScene(scene)

    def moveMonoCamera(self, coords):
        self.monoView.moveCamera(coords)

    def updateViews(self):
        self.panoView.update()
        self.monoView.update()
        self.resultView.update()

    def updateListView(self):
        self.labelListView.refreshList()

    def updataProgressView(self, val):
        self.progressView.setValue(val)
        QCoreApplication.processEvents()
    
    def refleshProcessEvent(self):
        QCoreApplication.processEvents()
    
    def closeEvent(self, event):
        if self.depthPred:
            self.depthPred.sess.close()
        event.accept()

    def keyPressEvent(self, event):
        print("main")
        key = event.key()
        #print(key)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
