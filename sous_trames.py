from PyQt5.QtCore import QVariant, QAbstractTableModel, QModelIndex
#from .abstract_model import AbstractGroupModel, AbstractGroupItem, DictItem, DictModel, AbstractConnector
#from .utils import *
import abstract_model
import utils

st_fields = ["name","descr"]
stModel = None
         
class STItem(abstract_model.DictItem):
    def __init__(self,st,descr):
        dict = {"name" : st,
                "descr" : descr}
        #assert(st_fields == dict.keys())
        super().__init__(dict)
        
    def checkItem(self):
        pass
        
    def equals(self,other):
        return (self.dict["name"] == other.dict["name"])
        
        
class STModel(abstract_model.DictModel):

    def __init__(self):
        super().__init__(self,st_fields)
        
    @staticmethod
    def mkItemFromDict(dict):
        utils.checkFields(st_fields,dict.keys())
        item = STItem(dict["name"],dict["descr"])
        return item
        
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