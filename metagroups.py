
from PyQt5.QtCore import QVariant, QAbstractTableModel, QModelIndex
from .abstract_model import AbstractGroupModel, AbstractGroupItem, DictItem, DictModel, AbstractConnector
from .utils import *

metagroups_fields = ["metagroup","descr"]
         
class Metagroup(DictItem):
    def __init__(self,metagroup,descr):
        dict = {"metagroup" : metagroup,
                "descr" : descr}
        #assert(metagroups_fields == dict.keys())
        super().__init__(dict)
        
    def checkItem(self):
        pass
        
    def equals(self,other):
        return (self.dict["metagroup"] == other.dict["metagroup"])
        
        
class MetagroupModel(DictModel):

    def __init__(self):
        super().__init__(self,metagroups_fields)
        
        
class Metagroups(AbstractConnector):

    def __init__(self,dlg):
        self.dlg = dlg
        self.metagroupsModel = MetagroupModel()
        super().__init__(self.metagroupsModel,self.dlg.metagroupsView,
                         self.dlg.metagroupsAdd,self.dlg.metagroupsRemove)
        
    def initGui(self):
        pass
        
    def connectComponents(self):
        super().connectComponents()

    def mkItem(self):
        name = self.dlg.metagroupsName.text()
        descr = self.dlg.metagroupsDescr.text()
        metagroupItem = Metagroup(name,descr)
        return metagroupItem
        
    # def removeMetagroup(self):
        # debug("removeMetagroup")
        # indices = self.dlg.metagroupsView.selectedIndexes()
        # debug(str(indices))
        # self.metagroupsModel.removeItems(indices)
        
# class Metagroups:

    # def __init__(self,dlg):
        # self.dlg = dlg
        # self.metagroupsModel = MetagroupModel()
        
    # def initGui(self):
        # pass
        
    # def connectComponents(self):
        # self.dlg.metagroupsView.setModel(self.metagroupsModel)
        # self.dlg.metagroupsAdd.clicked.connect(self.addMetagroup)
        # self.dlg.metagroupsRemove.clicked.connect(self.removeMetagroup)

    # def addMetagroup(self):
        # name = self.dlg.metagroupsName.text()
        # descr = self.dlg.metagroupsDescr.text()
        # metagroupItem = Metagroup(name,descr)
        # self.metagroupsModel.addItem(metagroupItem)
        # self.metagroupsModel.layoutChanged.emit()
        
    # def removeMetagroup(self):
        # debug("removeMetagroup")
        # indices = self.dlg.metagroupsView.selectedIndexes()
        # debug(str(indices))
        # self.metagroupsModel.removeItems(indices)