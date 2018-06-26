
import csv
import os

from PyQt5.QtCore import pyqtSlot
from qgis.gui import QgsFileWidget

import utils
import sous_trames
import classes
import params
import abstract_model
import qgsTreatments

frictionConnector = None
frictionModel = None
frictionFields = ["class_descr","class","code"]

@pyqtSlot()
def catchSTAdded(st_item):
    utils.debug("stAdded " + st_item.dict["name"])
    frictionModel.addSTItem(st_item)
    
@pyqtSlot()
def catchSTRemoved(name):
    frictionModel.removeSTFromName(name)
    
@pyqtSlot()
def catchClassAdded(class_item):
    utils.debug("classAdded " + class_item.dict["name"])
    frictionModel.addClassItem(class_item)
    
@pyqtSlot()
def catchClassRemoved(name):
    frictionModel.removeClassFromName(name)

class FrictionRowItem(abstract_model.DictItem):

    def __init__(self,dict):
        super().__init__(dict)
    
    def addSTCols(self,defaultVal):
        for st in sous_trames.getSTList():
            self.dict[st] = defaultVal
        self.recompute()
            
class FrictionModel(abstract_model.DictModel):

    def __init__(self):
        self.defaultVal = 100
        self.classes = []
        self.sous_trames = []
        self.fields = ["class_descr","class","code"]
        super().__init__(self,self.fields)
        
    def classExists(self,cls_name):
        for cls in self.classes:
            if cls["class"] == cls_name:
                return True
        return False
        
    def addClassItem(self,cls_item):
        new_row = {"class_descr" : cls_item.dict["descr"],
                   "class" : cls_item.dict["name"],
                   "code" : cls_item.dict["code"]}
        self.addSTCols(new_row)
        row_item = FrictionRowItem(new_row)
        if not self.classExists(cls_item.dict["name"]):
            #self.rows.append(new_row)
            self.addItem(row_item)
            self.layoutChanged.emit()
        
    def removeClassFromName(self,name):
        self.classes = [cls_item for cls_item in self.classes if cls_item.dict["name"] != name]
        for i in range(0,len(self.items)):
            if self.items[i].dict["class"] == name:
                del self.items[i]
                self.layoutChanged.emit()
                return
        
    def addSTCols(self,row):
        utils.debug("addSTCols")
        for st in sous_trames.getSTList():
            row[st] = self.defaultVal
            
    def addSTItem(self,st_item):
        utils.debug("addSTItem")
        st_name = st_item.dict["name"]
        if st_name not in self.fields:
            # for r in self.rows:
                # r[st_name] = self.defaultVal
            for i in self.items:
                i.dict[st_name] = self.defaultVal
                i.recompute()
            self.fields.append(st_name)
            frictionFields.append(st_name)
            self.sous_trames.append(st_item)
            self.layoutChanged.emit()
        
    def removeSTFromName(self,st_name):
        utils.debug("removeSTFromName " + st_name)
        self.sous_trames = [st_item for st_item in self.sous_trames if st_item.dict["name"] != st_name]
        self.removeField(st_name)
        frictionFields.remove(st_name)
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
                
    def applyReclassProcessing(self):
        utils.debug("applyReclass")
        self.createRulesFiles()
        for st_item in self.sous_trames:
            st_name = st_item.dict["name"]
            utils.debug("applyReclass " + st_name)
            st_rules_fname = st_item.getRulesPath()
            utils.checkFileExists(st_rules_fname)
            st_merged_fname = st_item.getMergedPath()
            utils.checkFileExists(st_merged_fname)
            st_friction_fname = st_item.getFrictionPath()
            qgsTreatments.applyReclassProcessing(st_merged_fname,st_friction_fname,st_rules_fname,st_name)
        
    def applyReclassGdal(self):
        utils.debug("applyReclassGdal")
        for st_item in self.sous_trames:
            st_merged_fname = st_item.getMergedPath()
            utils.checkFileExists(st_merged_fname)
            st_friction_fname = st_item.getFrictionPath()
            reclass_dict = {}
            for r in self.items:
                reclass_dict[r.dict['code']] = r.dict[st_item.dict["name"]]
            utils.debug(str(reclass_dict))
            #utils.debug("applyReclassGdal")
            qgsTreatments.applyReclassGdal(st_merged_fname,st_friction_fname,reclass_dict)
        
    def applyItems(self):
        #self.applyReclass()
        self.applyReclassGdal()
        
    def saveCSV(self,fname):
        with open(fname,"w", newline='') as f:
            writer = csv.DictWriter(f,fieldnames=self.fields,delimiter=';')
            writer.writeheader()
            for i in self.items:
                writer.writerow(i.dict)
                
    @classmethod
    def fromCSV(cls,fname):
        model = cls()
        model.classes = classes.classModel.items
        with open(fname,"r") as f:
            reader = csv.DictReader(f,fieldnames=frictionFields,delimiter=';')
            header = reader.fieldnames
            model.fields = header
            model.sous_trames = []
            for st in header[3:]:
                st_item = sous_trames.getSTByName(st)
                if not st_item:
                    utils.user_error("ST '" + st + "' does not exist")
                model.sous_trames.append(st_item)
            first_line = next(reader)
            for row in reader:
                item = FrictionRowItem(row)
                model.addItem(item)
        return model
    
        
    def fromXMLRoot(self,root):
        #model = cls()
        eraseFlag = True
        if eraseFlag:
            self.classes = classes.classModel.items
            self.sous_trames = sous_trames.stModel.items
            self.items = []
        for fr in root:
            item = FrictionRowItem(fr.attrib)
            self.addItem(item)
        self.layoutChanged.emit()
        #return model
           
class FrictionConnector(abstract_model.AbstractConnector):
    
    def __init__(self,dlg):
        global frictionModel
        self.dlg = dlg
        frictionModel = FrictionModel()
        super().__init__(frictionModel,self.dlg.frictionView,None,None)
        
    def initGui(self):
        self.dlg.frictionCsvFile.setStorageMode(QgsFileWidget.SaveFile)
        self.dlg.frictionCsvFile.setFilter("*.csv")
        self.dlg.frictionLoadFile.setStorageMode(QgsFileWidget.GetFile)
        self.dlg.frictionLoadFile.setFilter("*.csv")
        
    @pyqtSlot()
    def internCatchGroupAdded(grp):
        utils.debug("groupAdded2 " + grp)
        
    def connectComponents(self):
        sous_trames.stModel.stAdded.connect(catchSTAdded)
        sous_trames.stModel.stRemoved.connect(catchSTRemoved)
        classes.classModel.classAdded.connect(catchClassAdded)
        classes.classModel.classRemoved.connect(catchClassRemoved)
        super().connectComponents()
        self.dlg.frictionRun.clicked.connect(self.model.applyItems)
        # self.dlg.frictionSave.clicked.connect(self.saveCSV)
        # self.dlg.frictionLoad.clicked.connect(self.loadCSV)
        self.dlg.frictionCsvFile.fileChanged.connect(self.saveCSV)
        self.dlg.frictionLoadFile.fileChanged.connect(self.loadCSV)
        #sous_trames.stModel.groupAdded.connect(self.internCatchGroupAdded)
        
    def loadCSV(self,fname):
        global frictionModel, frictionFields
        #fname = self.dlg.frictionLoadFile.filePath()
        utils.checkFileExists(fname)
        new_model = self.model.fromCSV(fname)
        self.model = new_model
        frictionModel = new_model
        frictionFields = new_model.fields
        #self.view.setModel(self.model)
        self.connectComponents()
        self.model.layoutChanged.emit()
        frictionModel.layoutChanged.emit()
        
    def saveCSV(self,fname):
        #fname = self.dlg.frictionCsvFile.filePath()
        self.model.saveCSV(fname)
     
            
