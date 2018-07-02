
import copy
import subprocess
import xml.etree.ElementTree as ET

from PyQt5.QtCore import QModelIndex
from PyQt5.QtGui import QIcon

import abstract_model
import utils
import xmlUtils
import qgsUtils
import params
import sous_trames
import groups
from .qgsTreatments import *
from .config_parsing import *

fusion_fields = ["name","descr"]
#fusionConnector = None
        
class FusionModel(abstract_model.AbstractGroupModel):
    
    def __init__(self):
        self.st_groups = {}
        self.current_st = None
        self.current_model = None
        super().__init__(self,fusion_fields)
        
    def __str__(self):
        res = ""
        for st, grp_model in self.st_groups.items():
            res += st + " : "
            for g in grp_model.items:
                res += g.dict["name"] + ", "
            res += "\n"
        return res
        
    def getCurrModel(self):
        return self.st_groups[self.st_current_st]
        
    def setCurrentST(self,st):
        utils.debug("setCurrentST " + str(st))
        utils.debug(str(self))
        self.current_st = st
        if st not in self.st_groups: 
            self.loadAllGroups()
        else:
            self.current_model = self.st_groups[st]
            self.current_model.layoutChanged.emit()
        utils.debug(str(self))
        
    def loadAllGroups(self):
        utils.debug("[loadAllGroups]")
        self.current_model = groups.copyGroupModel(groups.groupsModel)
        self.st_groups[self.current_st] = self.current_model
        #self.current_model.layoutChanged.emit()
        self.layoutChanged.emit()
        
    def toXML(self,indent=""):
        xmlStr = indent + "<" + self.__class__.__name__ + ">\n"
        for st, grp in self.st_groups.items():
            xmlStr += indent + " <ST name=\"" + st + "\">\n"
            xmlStr += grp.toXML(indent=indent + "  ")
            xmlStr += indent + " </ST>"
        xmlStr += indent + "</" + self.__class__.__name__ + ">"
        return xmlStr
    
    def fromXMLRoot(self,root):
        #checkFields(fusion_fields,dict.keys())
        eraseFlag = xmlUtils.getNbChildren(root) > 0
        if eraseFlag:
            pass#self.items = []
        #fusion_model = cls() 
        for st_root in root:
            st_name = st_root.attrib["name"]
            self.current_st = st_name
            for grp in st_root:
                grp_model = parseModel(grp,True)
                if not grp_model:
                    utils.internal_error("Could not parse group model for " + st_name)
                self.st_groups[st_name] = grp_model
                self.current_model = grp_model
        #return fusion_model
        
    def applyItems(self):
        res = str(params.getResolution())
        extent_coords = params.getExtentCoords()
        #for st in reversed(list(self.st_groups.keys())):
        for st in self.st_groups.keys():
            st_item = sous_trames.getSTByName(st)
            groups = self.st_groups[st]
            utils.debug("apply fusion to " + st)
            utils.debug(str([g.dict["name"] for g in groups.items]))
            grp_args = [g.getRasterPath() for g in reversed(groups.items)]
            utils.debug(str(grp_args))
            out_path = st_item.getMergedPath()
            if os.path.isfile(out_path):
                qgsUtils.removeRaster(out_path)
            cmd_args = ['gdal_merge.bat',
                        '-o', out_path,
                        '-of', 'GTiff',
                        '-ot','Int32',
                        '-n', nodata_val,
                        '-a_nodata', nodata_val]
            #cmd_args += ['-ul_lr']
            #cmd_args += extent_coords
            #cmd_args += ['-ps',res,res]
            cmd_args = cmd_args + grp_args
            p = subprocess.Popen(cmd_args,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            out,err = p.communicate()
            utils.debug(str(p.args))
            utils.info(str(out))
            if err:
                utils.user_error(str(err))
            else:
                res_layer = qgsUtils.loadRasterLayer(out_path)
                QgsProject.instance().addMapLayer(res_layer)
            
    # def updateItems(self,i1,i2):
        # k = self.current_st
        # self.current_model.items[i1], self.current_model.items[i2] = self.current_model.items[i2], self.current_model.items[i1]
        # self.current_model.layoutChanged.emit()
        
    # def upgradeElem(self,idx):
        # row = idx.row()
        # utils.debug("upgradeElem " + str(row))
        # if row > 0:
            # self.swapItems(row -1, row)
        
    def downgradeElem(self,row):
        #row = idx.row()
        utils.debug("downgradeElem " + str(row))
        if row < len(self.current_model.items) - 1:
            self.swapItems(row, row + 1)
            
    def swapItems(self,i1,i2):
        self.current_model.swapItems(i1,i2)
        #self.current_model.layoutChanged.emit()
        self.layoutChanged.emit()
        
    def removeItems(self,index):
        utils.debug("[removeItems] nb of items = " + str(len(self.current_model.items))) 
        self.current_model.removeItems(index)
        self.current_model.layoutChanged.emit()
        
    def addItem(self,item):
        utils.debug("[addItemFusion]")
        self.current_model.addItem(item)
        self.current_model.layoutChanged.emit()
        
    def data(self,index,role):
        #utils.debug("[dataFusionModel]")
        return self.current_model.data(index,role)
        
    def rowCount(self,parent=QModelIndex()):
        if self.current_model:
            return self.current_model.rowCount(parent)
        else:
            return 0
        
    def columnCount(self,parent=QModelIndex()):
        if self.current_model:
            return self.current_model.columnCount(parent)
        else:
            return 0
        

class FusionConnector(abstract_model.AbstractConnector):
    
    def __init__(self,dlg):
        self.dlg = dlg
        self.models = {}
        fusionModel = FusionModel()
        super().__init__(fusionModel,self.dlg.fusionView,
                         None,self.dlg.fusionRemove)
                         
    def initGui(self):
        upIcon = QIcon(':plugins/eco_cont/icons/up-arrow.png')
        downIcon = QIcon(':plugins/eco_cont/icons/down-arrow.png')
        self.dlg.fusionUp.setIcon(upIcon)
        self.dlg.fusionDown.setIcon(downIcon)
                         
    def connectComponents(self):
        super().connectComponents()
        self.dlg.fusionST.setModel(sous_trames.stModel)
        #self.dlg.fusionGroup.setModel(groups.groupsModel)
        self.dlg.fusionST.currentTextChanged.connect(self.changeST)
        self.dlg.fusionLoadGroups.clicked.connect(self.model.loadAllGroups)
        self.dlg.fusionRun.clicked.connect(self.model.applyItems)
        self.dlg.fusionUp.clicked.connect(self.upgradeItem)
        self.dlg.fusionDown.clicked.connect(self.downgradeItem)
        
    def changeST(self,st):
        self.model.setCurrentST(st)
        self.dlg.fusionView.setModel(self.model.current_model)
        
    # def mkItem(self):
        # grp = self.dlg.fusionGroup.currentText()
        # grp_item = groups.groupsModel.getGroupByName(grp)
        # return grp_item   
        
    # def upgradeItem(self):
        # utils.debug("upgradeItem")
        # indices = self.view.selectedIndexes()
        # nb_indices = len(indices)
        # if nb_indices == 0:
            # utils.debug("no idx selected")
        # elif nb_indices == 1:
            # self.model.upgradeElem(indices[0])
        # else:
            # utils.warn("Several indices selected, please select only one")
            
    # def downgradeItem(self):
        # utils.debug("downgradeItem")
        # indices = self.view.selectedIndexes()
        # nb_indices = len(indices)
        # if nb_indices == 0:
            # utils.debug("no idx selected")
        # elif nb_indices == 1:
            # self.model.downgradeElem(indices[0])
        # else:
            # utils.warn("Several indices selected, please select only one")
        
# class FusionConnector:
    
    # def __init__(self,dlg):
        # self.dlg = dlg
        # self.models = {}
        # fusionModel = FusionModel()
        # super().__init__(fusionModel,self.dlg.fusionView,
        #                 self.dlg.fusionAdd,self.dlg.fusionRemove)
                         
    # def initGui(self):
        # pass
                         
    # def connectComponents(self):
        # super().connectComponents()
        # self.dlg.fusionST.setModel(sous_trames.stModel)
        # self.dlg.fusionGroup.setModel(groups.groupsModel)
        # self.dlg.fusionST.currentTextChanged.connect(self.changeST)
        # self.dlg.fusionLoadGroups.clicked.connect(self.model.loadAllGroups)
        
    # def changeST(self,st):
        # self.model.setCurrentST(st)
        # self.dlg.fusionView.setModel(self.model.current_model)
        
    # def mkItem(self):
        # grp = self.dlg.fusionGroup.currentText()
        # grp_item = groups.groupsModel.getGroupByName(grp)
        # return grp_item
