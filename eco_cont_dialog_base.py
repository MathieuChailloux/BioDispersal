# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'eco_cont_dialog_base.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_EcologicalContinuityDialogBase(object):
    def setupUi(self, EcologicalContinuityDialogBase):
        EcologicalContinuityDialogBase.setObjectName("EcologicalContinuityDialogBase")
        EcologicalContinuityDialogBase.resize(400, 300)
        self.button_box = QtWidgets.QDialogButtonBox(EcologicalContinuityDialogBase)
        self.button_box.setGeometry(QtCore.QRect(30, 240, 341, 32))
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.button_box.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.button_box.setObjectName("button_box")

        self.retranslateUi(EcologicalContinuityDialogBase)
        self.button_box.accepted.connect(EcologicalContinuityDialogBase.accept)
        self.button_box.rejected.connect(EcologicalContinuityDialogBase.reject)
        QtCore.QMetaObject.connectSlotsByName(EcologicalContinuityDialogBase)

    def retranslateUi(self, EcologicalContinuityDialogBase):
        _translate = QtCore.QCoreApplication.translate
        EcologicalContinuityDialogBase.setWindowTitle(_translate("EcologicalContinuityDialogBase", "Ecological Continuity"))

