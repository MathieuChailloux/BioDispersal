import os

from PyQt5.QtSql import QSqlRecord, QSqlTableModel, QSqlField
from PyQt5.QtCore import QVariant, QAbstractTableModel, QModelIndex
from qgis.gui import QgsFileWidget
import abstract_model
import utils
import qgsUtils
import params
import qgsTreatments
         
groups_fields = ["name","descr"]
groupsModel = None

def getGroupLayer(grp):
    groupItem = groupsModel.getGroupByName(out_name)
    group_layer = groupItem.getLayer()
    return group_layer
    
def getGroupByName(groups_name):
    for group in groupsModel.items:
        if group.name == groups_name:
            return group
    return None

def copyGroupModel(model):
    new_model = GroupModel()
    for i in model.items:
        new_model.addItem(i)
    return new_model
    
# def getGroupStorage(grp):
    # groupItem = groupsModel.getGroupByName(out_name)
    # group_storage = groupItem.dict["layer"]
    # return group_storage
    
class GroupItem(abstract_model.DictItem):
    
    def __init__(self,group,descr):
        dict = {"name" : group,
                "descr" : descr}
        #assert(groups_fields == dict.keys())
        self.name = group
        #self.in_layer = None
        self.vectorLayer = None
        self.rasterLayer = None
        super().__init__(dict)
        
    def checkItem(self):
        prefix="Group"
        utils.checkName(self,prefix)
        utils.checkDescr(self,prefix)
        
        
    def equals(self,other):
        return (self.dict["name"] == other.dict["name"])

    def getVectorPath(self):
        basename = self.name + "_vector.shp"
        return params.mkTmpPath(basename)
        
    def getRasterPath(self):
        basename = self.name + "_raster.tif"
        return params.mkTmpPath(basename)
        
    def saveVectorLayer(self):
        vector_path = self.getVectorPath()
        qgsUtils.writeShapefile(self.vectorLayer,vector_path)
            
    def applyRasterizationItem(self):
        utils.debug("[applyRasterizationItem]")
        field = "Code"
        group_name = self.dict["name"]
        in_path = self.getVectorPath()
        out_path = self.getRasterPath()
        qgsTreatments.applyRasterization(in_path,field,out_path)
        
class GroupModel(abstract_model.DictModel):

    def __init__(self):
        super().__init__(self,groups_fields)
        
    @staticmethod
    def mkItemFromDict(dict):
        utils.checkFields(groups_fields,dict.keys())
        item = GroupItem(dict["name"],dict["descr"])
        return item
        
    def getGroupByName(self,name):
        for i in self.items:
            if i.dict["name"] == name:
                return i
        None
        #utils.internal_error("Could not find groups '" + name + "'")
         

class GroupConnector(abstract_model.AbstractConnector):

    def __init__(self,dlg):
        self.dlg = dlg
        groupsModel = GroupModel()
        super().__init__(groupsModel,self.dlg.groupsView,
                        self.dlg.groupsAdd,self.dlg.groupsRemove)
        
    def initGui(self):
        pass
        
    def connectComponents(self):
        super().connectComponents()

    def mkItem(self):
        name = self.dlg.groupsName.text()
        descr = self.dlg.groupsDescr.text()
        groupsItem = GroupItem(name,descr)
        return groupsItem
         