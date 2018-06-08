
from PyQt5.QtCore import pyqtSlot

import utils
import sous_trames
import classes
import abstract_model

frictionModel = None

@pyqtSlot()
def catchSTAdded(st_item):
    utils.debug("stAdded " + st_item.dict["name"])
    frictionModel.addSTItem(st_item)
    
@pyqtSlot()
def catchClassAdded(class_item):
    utils.debug("classAdded " + class_item.dict["name"])
    frictionModel.addClassItem(class_item)

class FrictionRowItem(abstract_model.DictItem):

    def __init__(self,dict):
        super().__init__(dict)
    
    def addSTCols(self,defaultVal):
        for st in sous_trames.getSTList():
            self.dict[st] = defaultVal
        self.recompute()
            
class FrictionModel(abstract_model.DictModel):

    def __init__(self):
        self.rows = []
        self.defaultVal = 100
        self.classes = []
        self.sous_trames = []
        fields = ["class_descr","class","code"]
        super().__init__(self,fields)
        
    def addClassItem(self,cls_item):
        new_row = {"class_descr" : cls_item.dict["descr"],
                   "class" : cls_item.dict["name"],
                   "code" : cls_item.dict["code"]}
        self.addSTCols(new_row)
        row_item = FrictionRowItem(new_row)
        self.rows.append(new_row)
        self.addItem(row_item)
        self.layoutChanged.emit()
        
    def addSTCols(self,row):
        for st in sous_trames.getSTList():
            row[st] = self.defaultVal
            
    def addSTItem(self,st_item):
        st_name = st_item.dict["name"]
        for r in self.rows:
            r[st_name] = self.defaultVal
        for i in self.items:
            i.dict[st_name] = self.defaultVal
            i.recompute()
        self.fields.append(st_name)
        self.sous_trames.append(st_item)
        self.layoutChanged.emit()
        
    def createRulesFiles(self):
        utils.debug("createRulesFiles")
        for st_item in self.sous_trames:
            st_name = st_item.dict["name"]
            utils.debug("createRulesFiles " + st_name)
            st_rules_fname = st_item.getRulesPath()
            with open(st_rules_fname,"w") as f:
                for i in self.items:
                    in_class = i.dict["code"]
                    out_class = i.dict[st_name]
                    f.write(str(in_class) + " = " + str(out_class) + "\n")
                
        
        
        
    def applyItems(self):
        self.createRulesFiles() 
           
class FrictionConnector(abstract_model.AbstractConnector):
    
    def __init__(self,dlg):
        self.dlg = dlg
        frictionModel = FrictionModel()
        super().__init__(frictionModel,self.dlg.frictionView,None,None)
        
    def initGui(self):
        pass
        
    @pyqtSlot()
    def internCatchGroupAdded(grp):
        utils.debug("groupAdded2 " + grp)
        
    def connectComponents(self):
        sous_trames.stModel.stAdded.connect(catchSTAdded)
        classes.classModel.classAdded.connect(catchClassAdded)
        super().connectComponents()
        self.dlg.frictionRun.clicked.connect(self.model.applyItems)
        #sous_trames.stModel.groupAdded.connect(self.internCatchGroupAdded)
            
