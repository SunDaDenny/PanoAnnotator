
import sys
from PyQt5 import QtCore, QtGui, QtWidgets

from .PanoView import PanoView
from .MonoView import MonoView
from .ResultView import ResultView
from.LabelListView import LabelListView

class MainWindowUi(object):
    
    def setupUi(self, mainWindow):
        mainWindow.setObjectName("mainWindow")
        mainWindow.resize(1600, 900)

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
        mainWindow.setMenuBar(self.menubar)

        self.actionOpenFile = QtWidgets.QAction(mainWindow)
        self.actionOpenFile.setObjectName("actionOpenFile")
        self.menuOpen.addAction(self.actionOpenFile)
        self.menubar.addAction(self.menuOpen.menuAction())

        #####
        #Pano equalrectangular image view
        #####
        self.panoView = PanoView(self.centralWidget)
        self.panoView.setObjectName("panoView")
        self.panoView.setGeometry(QtCore.QRect(50, 50, 720, 360))
        self.panoView.setScaledContents(True)
        #self.panoView.setMinimumSize(QtCore.QSize(1024, 512))
        self.panoView.setText("PanoView Widget")
        self.panoView.setStyleSheet("#panoView { background-color: black }")

        #####
        #Pano monocular image view
        #####
        self.monoView = MonoView(self.centralWidget)
        self.monoView.setObjectName("monoView")
        self.monoView.setGeometry(QtCore.QRect(50, 450, 720, 360))

        #####
        #Result preview view
        #####
        self.resultView = ResultView(self.centralWidget)
        self.resultView.setObjectName("resultView")
        self.resultView.setGeometry(QtCore.QRect(820, 50 , 720, 360))

        #####
        #Data operation list
        ####
        self.labelListView = LabelListView(self.centralWidget)
        self.labelListView.setObjectName("LabelListView")
        self.labelListView.setGeometry(QtCore.QRect(820, 450, 360, 360))

        mainWindow.setCentralWidget(self.centralWidget)
       
        self.retranslateUi(mainWindow)
        QtCore.QMetaObject.connectSlotsByName(mainWindow)

    def retranslateUi(self, mainWindow):
        _translate = QtCore.QCoreApplication.translate
        mainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.menuOpen.setTitle(_translate("MainWindow", "Open"))
        self.actionOpenFile.setText(_translate("MainWindow", "Open File"))