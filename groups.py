
import os

from PyQt5.QtSql import QSqlRecord, QSqlTableModel, QSqlField
from PyQt5.QtCore import QVariant, QAbstractTableModel, QModelIndex
from qgis.gui import QgsFileWidget
#from .abstract_model import AbstractGroupModel, AbstractGroupItem, DictItem, DictModel, AbstractConnector
import abstract_model
# import abstract_model
#from .utils import *
import utils
#from .qgsUtils import *
import qgsUtils
         
groups_fields = ["group","descr","metagroup","layer"]
groupsModel = None

def getGroupLayer(grp):
    groupItem = groupsModel.getGroupByName(out_name)
    group_layer = groupItem.getLayer()
    return group_layer

def getGroupStorage(grp):
    groupItem = groupsModel.getGroupByName(out_name)
    group_storage = groupItem.dict["layer"]
    return group_storage
    
class GroupItem(abstract_model.DictItem):
    
    def __init__(self,group,descr,metagroup,layer):
        dict = {"group" : group,
                "descr" : descr,
                "metagroup" : metagroup,
                "layer" : layer}
        #assert(groups_fields == dict.keys())
        self.name = group
        if layer == "memory":
            self.is_memory = True
            self.path = utils.tmpDir + "/" + group
        else:
            self.is_memory = False
            self.path = layer
        self.layer = None
        super().__init__(dict)        
        
    def checkItem(self):
        pass
        
    def equals(self,other):
        return (self.dict["group"] == other.dict["group"])
        
    def instantiateLayer(self,inLayer=None,geomType=None,crs=None):
        if self.layer:
            utils.debug("Layer '" + self.name + " already exists")
        elif self.is_memory:
            self.layer = qgsUtils.createLayerFromExisting(inLayer,self.name,geomType,crs)
        elif os.path.isfile(self.path):
            self.layer = qgsUtils.loadVectorLayer(self.path)
        else:
            self.layer = qgsUtils.createLayerFromExisting(inLayer,self.name,geomType,crs)
            qgsUtils.writeShapefile(self.layer,self.path)
            
        
    def getLayer(self):
        name = self.dict["group"]
        layer = self.dict["layer"]
        if layer == "memory":
            res = qgsUtils.getLoadedLayerByName(name)
        elif os.path.isfile(layer):
            res = qgsUtils.loadVectorLayer(layer)
        else:
            return None
            
    def getLayerForce(self):
        name = self.dict["group"]
        layer = self.dict["layer"]
        if layer == "memory":
            res = qgsUtils.getLoadedLayerByName(name)
        elif os.path.isfile(layer):
            res = qgsUtils.loadVectorLayer(layer)
        else:
            utils.user_error("Could not find layer for group '" + name + "'")
        return res
            
    def mkTmpLayerPath(self):
        tmpPath = utils.tmpDir + "/" + self.dict["group"]
        return tmpPath
        
    def saveLayerAsFile(self):
        #grp = self.dict["group"]
        #layer = self.getLayer()
        if self.layer:
            qgsUtils.writeShapefile(self.layer,self.path)
        else:
            utils.user_error("Could not find layer for group '" + self.name + "'")
        
    def getAndCreateLayerPath(self):
        name = self.dict["group"]
        if self.is_memory:
            loadedLayer = qgsUtils.getLoadedLayerByName(name)
            if loadedLayer:
                uri = loadedLayer.dataProvider().dataSourceUri()
                if uri:
                    return qgsUtils.pathOfLayer(loadedLayer)
                else:
                    tmp_path = self.mkTmpLayerPath()
            
    # def getOrCreateLayer(self,init_layer):
        # name = self.dict["group"]
        # layer = self.dict["layer"]
        # if layer = "memory":
            # res = getLoadedLayerByName(name)
            # if not res:
                # res = createLayerFromExistingOne(init_layer)
        # elif os.path.isfile(layer):
            # res = loadVectorLayer(layer)
        # if not res:
            # res = createLayerFromExistingOne(init_layer)
        # if layer != "memory":
            # writeShapefile(res,layer)
        # return res
        
        
class GroupModel(abstract_model.DictModel):

    def __init__(self):
        super().__init__(self,groups_fields)
        
    @staticmethod
    def mkItemFromDict(dict):
        utils.checkFields(groups_fields,dict.keys())
        item = GroupItem(dict["group"],dict["descr"],dict["metagroup"],dict["layer"])
        return item
        
    def getGroupByName(self,name):
        for i in self.items:
            if i.dict["group"] == name:
                return i
        utils.internal_error("Could not find group '" + name + "'")
         
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
         


class GroupConnector(abstract_model.AbstractConnector):

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
        