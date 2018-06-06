from PyQt5.QtCore import QVariant, QAbstractTableModel, QModelIndex
from .abstract_model import AbstractGroupModel, AbstractGroupItem, DictItem, DictModel, AbstractConnector
from .utils import *

st_fields = ["name","descr"]
st_model = None
         
class STItem(DictItem):
    def __init__(self,st,descr):
        dict = {"name" : st,
                "descr" : descr}
        #assert(st_fields == dict.keys())
        super().__init__(dict)
        
    def checkItem(self):
        pass
        
    def equals(self,other):
        return (self.dict["name"] == other.dict["name"])
        
        
class STModel(DictModel):

    def __init__(self):
        super().__init__(self,st_fields)
        
    @staticmethod
    def mkItemFromDict(dict):
        checkFields(st_fields,dict.keys())
        item = STItem(dict["name"],dict["descr"])
        return item
        
class STs(AbstractConnector):

    def __init__(self,dlg):
        self.dlg = dlg
        self.stModel = STModel()
        super().__init__(self.stModel,self.dlg.groupView,
                         self.dlg.groupAdd,self.dlg.groupRemove)
        
    def initGui(self):
        pass
        
    def connectComponents(self):
        super().connectComponents()

    def mkItem(self):
        name = self.dlg.groupName.text()
        descr = self.dlg.groupDescr.text()
        stItem = STItem(name,descr)
        return stItem