
import copy

from PyQt5.QtCore import QModelIndex

import abstract_model
import utils
import qgsUtils
import params
import sous_trames
import groups

fusion_fields = ["name","descr"]
        
class FusionModel(abstract_model.AbstractGroupModel):
    
    def __init__(self):
        self.st_groups = {}
        self.current_st = None
        self.current_model = None
        super().__init__(self,fusion_fields)
        
    def getCurrModel(self):
        return self.st_groups[self.st_current_st]
        
    def setCurrentST(self,st):
        self.current_st = st
        if st not in self.st_groups:
            self.loadAllGroups()
        else:
            self.current_model = self.st_groups[st]
            self.layoutChanged.emit()
        
    def loadAllGroups(self):
        self.current_model = groups.copyGroupModel(groups.groupsModel)
        self.st_groups[self.current_st] = self.current_model
        #self.layoutToBeChanged.emit()
        self.layoutChanged.emit()
        
    # def addST(self,st):
        # self.st_groups[st] = groups.groupsModel.copy()
        
    def removeItems(self,index):
        utils.debug("[removeItems] nb of items = " + str(len(self.current_model.items))) 
        self.current_model.removeItems(index)
        self.current_model.layoutChanged.emit()
        self.layoutChanged.emit()
        
    def addItem(self,item):
        utils.debug("[addItemFusion]")
        self.current_model.addItem(item)
        self.current_model.layoutChanged.emit()
        self.layoutChanged.emit()
        
    def data(self,index,role):
        utils.debug("[dataFusionModel]")
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
                         self.dlg.fusionAdd,self.dlg.fusionRemove)
                         
    def initGui(self):
        pass
                         
    def connectComponents(self):
        super().connectComponents()
        self.dlg.fusionST.setModel(sous_trames.stModel)
        self.dlg.fusionGroup.setModel(groups.groupsModel)
        self.dlg.fusionST.currentTextChanged.connect(self.changeST)
        self.dlg.fusionLoadGroups.clicked.connect(self.model.loadAllGroups)
        
    def changeST(self,st):
        self.model.setCurrentST(st)
        self.dlg.fusionView.setModel(self.model.current_model)
        
    def mkItem(self):
        grp = self.dlg.fusionGroup.currentText()
        grp_item = groups.groupsModel.getGroupByName(grp)
        return grp_item   
        
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
