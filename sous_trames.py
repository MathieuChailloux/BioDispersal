from PyQt5.QtCore import QVariant, QAbstractTableModel, QModelIndex, pyqtSignal
#from .abstract_model import AbstractGroupModel, AbstractGroupItem, DictItem, DictModel, AbstractConnector
#from .utils import *
import params
import abstract_model
import utils

st_fields = ["name","descr"]
stModel = None
         
def getSTByName(st_name):
    for st in stModel.items:
        if st.name == st_name:
            return st
    return None
         
def getSTList():
    return [st.dict["name"] for st in stModel.items]
         
class STItem(abstract_model.DictItem):
    def __init__(self,st,descr):
        dict = {"name" : st,
                "descr" : descr}
        self.name = st
        #assert(st_fields == dict.keys())
        super().__init__(dict)
        
    def checkItem(self):
        pass
        
    def equals(self,other):
        return (self.dict["name"] == other.dict["name"])
        
    def getMergedPath(self):
        basename = self.name + "_merged.tif"
        return params.mkTmpPath(basename)
        
    def getRulesPath(self):
        basename = self.name + "_rules.txt"
        return params.mkTmpPath(basename)
        
        
class STModel(abstract_model.DictModel):

    stAdded = pyqtSignal('PyQt_PyObject')

    def __init__(self):
        super().__init__(self,st_fields)
        
    @staticmethod
    def mkItemFromDict(dict):
        utils.checkFields(st_fields,dict.keys())
        item = STItem(dict["name"],dict["descr"])
        return item
        
    def addItem(self,item):
        super().addItem(item)
        self.stAdded.emit(item)
        
class STConnector(abstract_model.AbstractConnector):

    def __init__(self,dlg):
        self.dlg = dlg
        self.stModel = STModel()
        super().__init__(self.stModel,self.dlg.stView,
                         self.dlg.stAdd,self.dlg.stRemove)
        
    def initGui(self):
        pass
        
    def connectComponents(self):
        super().connectComponents()

    def mkItem(self):
        name = self.dlg.stName.text()
        descr = self.dlg.stDescr.text()
        stItem = STItem(name,descr)
        return stItem