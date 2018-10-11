import os

from PyQt5.QtSql import QSqlRecord, QSqlTableModel, QSqlField
from PyQt5.QtCore import QVariant, QAbstractTableModel, QModelIndex, pyqtSignal
from qgis.gui import QgsFileWidget
import abstract_model
import utils
import qgsUtils
import params
import qgsTreatments
import classes
         
groups_fields = ["name","descr","geom"]
#groupsConnector = None
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
    
    def __init__(self,group,descr,geom):
        if not geom:
            geom = "No geometry"
        dict = {"name" : group,
                "descr" : descr,
                "geom" : geom}
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
        
    def checkGeom(self,geom):
        if self.dict["geom"] != geom:
            utils.user_error("Incompatible geometries for group '"
                             + self.dict["name"] + "' : "
                             + self.dict["geom"] + " vs " + str(geom))
        
    def equals(self,other):
        return (self.dict["name"] == other.dict["name"])

    def getGroupPath(self):
        params.checkWorkspaceInit()
        groups_path = os.path.join(params.params.workspace,"Groupes")
        if not os.path.isdir(groups_path):
            utils.info("Creating groups directory '" + groups_path + "'")
            os.makedirs(groups_path)
        group_path = os.path.join(groups_path,self.name)
        if not os.path.isdir(group_path):
            utils.info("Creating group directory '" + group_path + "'")
            os.makedirs(group_path)
        return group_path
        
    def getVectorPath(self):
        basename = self.name + "_vector.shp"
        grp_path = self.getGroupPath()
        return os.path.join(grp_path,basename)
        
    def getRasterPath(self):
        basename = self.name + "_raster.tif"
        grp_path = self.getGroupPath()
        return os.path.join(grp_path,basename)
        
    def getRasterTmpPath(self):
        basename = self.name + "_raster_tmp.tif"
        grp_path = self.getGroupPath()
        return os.path.join(grp_path,basename)
        
    def saveVectorLayer(self):
        vector_path = self.getVectorPath()
        qgsUtils.writeShapefile(self.vectorLayer,vector_path)
        
    def getReclassDict(self):
        reclass_dict = {}
        for cls_item in classes.classModel.items:
            group_name = self.dict["name"]
            if cls_item.dict["group"] == group_name:
                class_name = cls_item.dict["name"]
                if group_name not in class_name:
                    utils.internal_error("Inconsistent class/group : " + str(class_name) + " - " + str(group_name))
                len_grp = len(group_name)
                assert(len(class_name) > len_grp)
                val = class_name[len_grp+1:]
                reclass_dict[val] = cls_item.dict["code"]
        assert(len(reclass_dict) > 0)
        return reclass_dict
            
    def applyRasterizationItem(self):
        utils.debug("[applyRasterizationItem]")
        field = "Code"
        group_name = self.dict["name"]
        in_path = self.getVectorPath()
        out_path = self.getRasterPath()
        params.checkInit()
        resolution = params.getResolution()
        extent_path = params.getExtentLayer()
        qgsTreatments.applyRasterization(in_path,field,out_path,resolution,extent_path,True,True)
        
class GroupModel(abstract_model.DictModel):

    groupAdded = pyqtSignal('PyQt_PyObject')
    groupRemoved = pyqtSignal('PyQt_PyObject')

    def __init__(self):
        super().__init__(self,groups_fields)
        
    @staticmethod
    def mkItemFromDict(dict):
        utils.checkFields(groups_fields,dict.keys())
        item = GroupItem(dict["name"],dict["descr"],dict["geom"])
        return item
        
    def getGroupByName(self,name):
        for i in self.items:
            if i.dict["name"] == name:
                return i
        None
        #utils.internal_error("Could not find groups '" + name + "'")
             
    def groupExists(self,name):
        grp_item = self.getGroupByName(name)
        return (grp_item != None)
             
    def addItem(self,item):
        super().addItem(item)
        self.groupAdded.emit(item)
        
    def removeItems(self,indexes):
        names = [self.items[idx.row()].dict["name"] for idx in indexes]
        super().removeItems(indexes)
        for n in names:
            self.groupRemoved.emit(n)
            
    def removeGroupFromName(self,name):
        self.items = [item for item in self.items if item.dict["name"] != name]
        self.layoutChanged.emit()

class GroupConnector(abstract_model.AbstractConnector):

    def __init__(self,dlg):
        self.dlg = dlg
        groupsModel = GroupModel()
        super().__init__(groupsModel,self.dlg.groupsView,
                        self.dlg.selectionGroupAdd,self.dlg.groupsRemove)
        # super().__init__(groupsModel,self.dlg.groupsView,
                        # self.dlg.groupsAdd,self.dlg.groupsRemove)
        
    def initGui(self):
        pass#self.dlg.groupFrame.hide()
        
    def connectComponents(self):
        super().connectComponents()
        self.dlg.selectionGroupCombo.currentTextChanged.connect(self.setGroupName)

    def mkItem(self):
        name = self.dlg.selectionGroupName.text()
        self.dlg.selectionGroupCombo.setCurrentText(name)
        descr = self.dlg.selectionGroupDescr.text()
        selection_in_layer = self.dlg.selectionInLayerCombo.currentLayer()
        if selection_in_layer:
            if self.dlg.selectionLayerFormatVector.isChecked():
                geom = qgsUtils.getLayerSimpleGeomStr(selection_in_layer)
            else:
                geom = "Raster"
            groupsItem = GroupItem(name,descr,geom)
            return groupsItem
        utils.user_error("No layer selected")
        
    def addItem(self,item):
        super().addItem()
        self.dlg.selectionGroupCombo.setCurrentIndex(len(self.model.items)-1)
        
    def setGroupName(self,text):
        utils.debug("setGroupName " + str(text))
        grp_item = getGroupByName(text)
        self.dlg.selectionGroupName.setText(grp_item.dict["name"])
        self.dlg.selectionGroupDescr.setText(grp_item.dict["descr"])
        
