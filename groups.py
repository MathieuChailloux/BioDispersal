
from PyQt5.QtSql import QSqlRecord, QSqlTableModel, QSqlField
from PyQt5.QtCore import QVariant, QAbstractTableModel, QModelIndex
from qgis.gui import QgsFileWidget
from .abstract_model import AbstractGroupModel, AbstractGroupItem, DictItem, DictModel, AbstractConnector
from .utils import *
         
groups_fields = ["group","descr","metagroup","layer"]

class GroupItem(DictItem):
    
    def __init__(self,group,descr,metagroup,layer):
        dict = {"group" : group,
                "descr" : descr,
                "metagroup" : metagroup,
                "layer" : layer}
        #assert(groups_fields == dict.keys())
        super().__init__(dict)
        
    def checkItem(self):
        pass
        
    def equals(self,other):
        return (self.dict["group"] == other.dict["group"])
        
class GroupModel(DictModel):

    def __init__(self):
        super().__init__(self,groups_fields)
        
         
# class Groups(AbstractConnector):

    # def __init__(self,dlg,metagroupsModel):
        # self.dlg = dlg
        # self.groupsModel = GroupModel()
        # self.metagroupsModel = metagroupsModel
        # super().__init__(
        
    # def setMetagroupsModel(self,model):
        # self.metagroupsModel = model
        
    # def initGui(self):
        # pass
        
    # def connectComponents(self):
        # self.dlg.groupsView.setModel(self.groupsModel)
        # self.dlg.groupsAdd.clicked.connect(self.addGroup)
        # self.dlg.groupsRemove.clicked.connect(self.removeGroup)
        # self.dlg.groupsMetagroup.setModel(self.metagroupsModel)
        # self.metagroupsModel.layoutChanged.connect(self.updateMetagroups)

    # def mkItem(self):
        # name = self.dlg.groupsName.text()
        # descr = self.dlg.groupsDescr.text()
        # layer = self.dlg.groupsLayer.filePath()
        # if not layer:
            # layer = "memory"
        # metagroup = self.dlg.groupsMetagroup.currentText()
        # groupItem = GroupItem(name,descr,metagroup,layer)
        # return groupItem
        
    # def addGroup(self):
        # name = self.dlg.groupsName.text()
        # descr = self.dlg.groupsDescr.text()
        # layer = self.dlg.groupsLayer.filePath()
        # if not layer:
            # layer = "memory"
        # metagroup = self.dlg.groupsMetagroup.currentText()
        # groupItem = GroupItem(name,descr,metagroup,layer)
        # self.groupsModel.addItem(groupItem)
        # self.groupsModel.layoutChanged.emit()
        
    # def removeGroup(self):
        # debug("removegroup")
        # indices = self.dlg.groupsView.selectedIndexes()
        # debug(str(indices))
        # self.groupsModel.removeItems(indices)
         


class Groups(AbstractConnector):

    def __init__(self,dlg,metagroupsModel):
        self.dlg = dlg
        self.groupsModel = GroupModel()
        self.metagroupsModel = metagroupsModel
        super().__init__(self.groupsModel,self.dlg.groupsView,
                        self.dlg.groupsAdd,self.dlg.groupsRemove)
        
    def setMetagroupsModel(self,model):
        self.metagroupsModel = model
        
    def initGui(self):
        pass
        
    def connectComponents(self):
        super().connectComponents()
        self.dlg.groupsMetagroup.setModel(self.metagroupsModel)
        self.dlg.groupsLayer.setStorageMode(QgsFileWidget.SaveFile)
        #self.metagroupsModel.layoutChanged.connect(self.updateMetagroups)

    def mkItem(self):
        name = self.dlg.groupsName.text()
        descr = self.dlg.groupsDescr.text()
        layer = self.dlg.groupsLayer.filePath()
        if not layer:
            layer = "memory"
        metagroup = self.dlg.groupsMetagroup.currentText()
        groupItem = GroupItem(name,descr,metagroup,layer)
        return groupItem
         
    # def updateMetagroups(self):
        # items=[mg.dict["metagroup"] for mg in self.metagroupsModel.items]
        # self.dlg.groupsMetagroup.addItems(items)
        