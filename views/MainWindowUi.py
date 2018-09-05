from PyQt5 import QtCore, QtGui, QtWidgets

from .PanoView import PanoView
from .MonoView import MonoView
from .ResultView import ResultView
from .LabelListView import LabelListView

class MainWindowUi(object):
    
    def setupUi(self, mainWindow):
        mainWindow.setObjectName("mainWindow")
        mainWindow.resize(1470, 900)

        self.centralWidget = QtWidgets.QWidget(mainWindow)
        self.centralWidget.setObjectName("centralWidget")

        #####
        #Menu bar seting
        #####
        self.menubar = QtWidgets.QMenuBar(mainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1600, 30))
        self.menubar.setObjectName("menubar")
        mainWindow.setMenuBar(self.menubar)

        self.menuOpen = QtWidgets.QMenu(self.menubar)
        self.menuOpen.setObjectName("menuOpen")
        self.actionOpenFile = QtWidgets.QAction(mainWindow)
        self.actionOpenFile.setObjectName("actionOpenFile")
        self.menuOpen.addAction(self.actionOpenFile)
        self.menubar.addAction(self.menuOpen.menuAction())

        self.menuSave = QtWidgets.QMenu(self.menubar)
        self.menuSave.setObjectName("menuSave")
        self.actionSaveFile = QtWidgets.QAction(mainWindow)
        self.actionSaveFile.setObjectName("actionSaveFile")
        self.menuSave.addAction(self.actionSaveFile)
        self.menubar.addAction(self.menuSave.menuAction())

        #####
        #Pano equalrectangular image view
        #####
        self.panoView = PanoView(self.centralWidget)
        self.panoView.setObjectName("panoView")
        self.panoView.setGeometry(QtCore.QRect(25, 25, 800, 400))
        self.panoView.setScaledContents(True)
        #self.panoView.setMinimumSize(QtCore.QSize(1024, 512))
        self.panoView.setText("PanoView Widget")
        self.panoView.setStyleSheet("#panoView { background-color: black }")

        #####
        #Pano monocular image view
        #####
        self.monoView = MonoView(self.centralWidget)
        self.monoView.setObjectName("monoView")
        self.monoView.setGeometry(QtCore.QRect(25, 450, 800, 400))

        #####
        #Result preview view
        #####
        self.resultView = ResultView(self.centralWidget)
        self.resultView.setObjectName("resultView")
        self.resultView.setGeometry(QtCore.QRect(850, 25 , 600, 400))

        #####
        #Data operation list
        ####
        self.labelListView = LabelListView(self.centralWidget)
        self.labelListView.setObjectName("ProgressView")
        self.labelListView.setGeometry(QtCore.QRect(850, 450, 600, 350))


        self.progressView = QtWidgets.QProgressBar(self.centralWidget)
        self.progressView.setObjectName("LabelListView")
        self.progressView.setGeometry(QtCore.QRect(850, 810, 600, 40))


        mainWindow.setCentralWidget(self.centralWidget)
       
        self.retranslateUi(mainWindow)
        QtCore.QMetaObject.connectSlotsByName(mainWindow)

    def retranslateUi(self, mainWindow):
        _translate = QtCore.QCoreApplication.translate
        mainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.menuOpen.setTitle(_translate("MainWindow", "Open"))
        self.actionOpenFile.setText(_translate("MainWindow", "Open File"))
        self.menuSave.setTitle(_translate("MainWindow", "Save"))
        self.actionSaveFile.setText(_translate("MainWindow", "Save File"))