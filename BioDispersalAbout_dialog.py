
import os

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets

#FORM_CLASS_TEST, _ = uic.loadUiType(os.path.join(
#    os.path.dirname(__file__), 'BioDispersalAbout_dialog_base.ui'))
   
from BioDispersalAbout_dialog_base import Ui_BioDispersalAbout

class BioDispersalAboutDialog(QtWidgets.QDialog,Ui_BioDispersalAbout):

    def __init__(self,parent=None):
        super(BioDispersalAboutDialog,self).__init__(parent)
        self.setupUi(self)
        
