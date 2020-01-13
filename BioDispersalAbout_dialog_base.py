# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'BioDispersalAbout_dialog_base.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_BioDispersalAbout(object):
    def setupUi(self, BioDispersalAbout):
        BioDispersalAbout.setObjectName("BioDispersalAbout")
        BioDispersalAbout.resize(714, 424)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(BioDispersalAbout.sizePolicy().hasHeightForWidth())
        BioDispersalAbout.setSizePolicy(sizePolicy)
        self.gridLayout = QtWidgets.QGridLayout(BioDispersalAbout)
        self.gridLayout.setObjectName("gridLayout")
        self.label_2 = QtWidgets.QLabel(BioDispersalAbout)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setMaximumSize(QtCore.QSize(102, 25))
        self.label_2.setText("")
        self.label_2.setPixmap(QtGui.QPixmap(":/plugins/BioDispersal/icons/logoINRAE.png"))
        self.label_2.setScaledContents(True)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(BioDispersalAbout)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy)
        self.label_3.setMaximumSize(QtCore.QSize(136, 68))
        self.label_3.setText("")
        self.label_3.setPixmap(QtGui.QPixmap(":/plugins/BioDispersal/icons/logoTetis.png"))
        self.label_3.setScaledContents(True)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 0, 1, 1, 1)
        self.label_4 = QtWidgets.QLabel(BioDispersalAbout)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy)
        self.label_4.setMaximumSize(QtCore.QSize(105, 68))
        self.label_4.setText("")
        self.label_4.setPixmap(QtGui.QPixmap(":/plugins/BioDispersal/icons/logoCRTVB.png"))
        self.label_4.setScaledContents(True)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 0, 2, 1, 1)
        self.label_5 = QtWidgets.QLabel(BioDispersalAbout)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_5.sizePolicy().hasHeightForWidth())
        self.label_5.setSizePolicy(sizePolicy)
        self.label_5.setMaximumSize(QtCore.QSize(53, 68))
        self.label_5.setText("")
        self.label_5.setPixmap(QtGui.QPixmap(":/plugins/BioDispersal/icons/logoMTES.png"))
        self.label_5.setScaledContents(True)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 0, 3, 1, 1)
        self.label = QtWidgets.QLabel(BioDispersalAbout)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setWordWrap(True)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 1, 0, 1, 4)

        self.retranslateUi(BioDispersalAbout)
        QtCore.QMetaObject.connectSlotsByName(BioDispersalAbout)

    def retranslateUi(self, BioDispersalAbout):
        _translate = QtCore.QCoreApplication.translate
        BioDispersalAbout.setWindowTitle(_translate("BioDispersalAbout", "BioDispersal - About"))
        self.label.setText(_translate("BioDispersalAbout", "<html><head/><body><p>BioDispersal is a QGIS 3 plugin (GNU GPLv3 licence) computing potential dispersal areas based on landscape permeability. It defines a 7 step procedure easing data preparation and performing effective dispersal computation.</p><p>BioDispersal has been developped by research unit UMR TETIS at INRAE in 2018. This project has been funded by French ministry of ecology for the ecological network resource center.</p><p><span style=\" font-style:italic;\">Designer / Developper </span>: Mathieu Chailloux</p><p><span style=\" font-style:italic;\">Project initiator</span> : Jennifer Amsallem</p><p><span style=\" font-style:italic;\">Links:</span> :</p><p>- BioDispersal GitHub: <a href=\"https://github.com/MathieuChailloux/BioDispersal\"><span style=\" text-decoration: underline; color:#0000ff;\">https://github.com/MathieuChailloux/BioDispersal</span></a></p><p>- BioDispersal bugtracker: <a href=\"https://github.com/MathieuChailloux/BioDispersal/issues\"><span style=\" text-decoration: underline; color:#0000ff;\">https://github.com/MathieuChailloux/BioDispersal/issues</span></a></p><p>- French ecological network resource center: <a href=\"http://www.trameverteetbleue.fr/\"><span style=\" text-decoration: underline; color:#0000ff;\">http://www.trameverteetbleue.fr/</span></a></p><p>- UMR TETIS: <a href=\"https://tetis.teledetection.fr\"><span style=\" text-decoration: underline; color:#0000ff;\">https://tetis.teledetection.fr</span></a></p><p>- INRAE: <a href=\"https://www.inrae.fr/\"><span style=\" text-decoration: underline; color:#0000ff;\">https://www.inrae.fr/</span></a></p></body></html>"))

