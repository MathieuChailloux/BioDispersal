import os

from PyQt5.QtSql import QSqlRecord, QSqlTableModel, QSqlField
from PyQt5.QtCore import QVariant, QAbstractTableModel, QModelIndex
from qgis.gui import QgsFileWidget
import abstract_model
import utils
import qgsUtils
import params
         
class_fields = ["code","name","descr"]
classModel = None

def getClassLayer(grp):
    clsItem = classModel.getClassByName(out_name)
    cls_layer = clsItem.getLayer()
    return cls_layer
    
def getClassByName(class_name):
    for cls in classModel.items:
        if cls.name == class_name:
            return cls
    return None

# def getClassStorage(grp):
    # clsItem = classModel.getClassByName(out_name)
    # cls_storage = clsItem.dict["layer"]
    # return cls_storage
    
class ClassItem(abstract_model.DictItem):
    
    def __init__(self,cls,descr,code):
        utils.debug("init with code " + str(code))
        if code == None:
            code = classModel.getFreeCode()
            utils.debug("new code = " + str(code))
        dict = {"code": code,
                "name" : cls,
                "descr" : descr}
        #assert(class_fields == dict.keys())
        self.name = cls
        super().__init__(dict)
        
    def checkItem(self):
        pass
        
    def equals(self,other):
        return (self.dict["name"] == other.dict["name"])
            
        
class ClassModel(abstract_model.DictModel):

    def __init__(self):
        super().__init__(self,class_fields)
        
    @staticmethod
    def mkItemFromDict(dict):
        utils.checkFields(class_fields,dict.keys())
        item = ClassItem(dict["name"],dict["descr"])
        return item
        
    def getClassByName(self,name):
        for i in self.items:
            if i.dict["name"] == name:
                return i
        None
        #utils.internal_error("Could not find class '" + name + "'")
        
    def codeExists(self,n):
        for i in self.items:
            if i.dict["code"] == n:
                return True
        return False
            
    def getFreeCode(self):
        cpt = 1
        while True:
            if not self.codeExists(cpt):
                return cpt
            cpt += 1
         

class ClassConnector(abstract_model.AbstractConnector):

    def __init__(self,dlg):
        self.dlg = dlg
        classModel = ClassModel()
        super().__init__(classModel,self.dlg.classView,
                        self.dlg.classAdd,self.dlg.classRemove)
        
    def initGui(self):
        pass
        
    def connectComponents(self):
        super().connectComponents()

    def mkItem(self):
        name = self.dlg.className.text()
        descr = self.dlg.classDescr.text()
        classItem = ClassItem(name,descr)
        return classItem
         