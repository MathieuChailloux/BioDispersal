
from .abstract_model import AbstractGroupModel, AbstractGroupItem, DictItem, DictModel, AbstractConnector
from .utils import *

buffer_fields = ["in_group","buffer","out_group"]

class BufferItem(DictItem):
    
    def __init__(self,in_group,buffer,out_group):
        dict = {"in_group" : in_group,
                "buffer" : buffer,
                "out_group" : out_group}
        super().__init__(dict)
        
    def equals(self,other):
        return (self.dict == other.dict)
        
class BufferModel(DictModel):
    
    def __init__(self):
        super().__init__(self,buffer_fields)
        
class BufferConnector(AbstractConnector):

    def __init__(self,dlg,groupsModel):
        self.dlg = dlg
        self.bufferModel = BufferModel()
        self.groupsModel = groupsModel
        super().__init__(self.bufferModel,self.dlg.bufferView,
                        self.dlg.bufferAdd,self.dlg.bufferRemove)
                        
    def setGroupsModel(self,model):
        self.groupsModel = model
        
    def initGui(self):
        pass
        
    def connectComponents(self):
        super().connectComponents()
        self.dlg.bufferInGroup.setModel(self.groupsModel)
        self.dlg.bufferOutGroup.setModel(self.groupsModel)
        
    def mkItem(self):
        in_group = self.dlg.bufferInGroup.currentText()
        buffer_val = self.dlg.bufferValue.value()
        out_group = self.dlg.bufferOutGroup.currentText()
        bufferItem = BufferItem(in_group,buffer_val,out_group)
        return bufferItem