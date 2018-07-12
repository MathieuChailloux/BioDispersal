
from .abstract_model import AbstractGroupModel, AbstractGroupItem, DictItem, DictModel, AbstractConnector
from .utils import *
from .qgsUtils import *
import groups

buffer_fields = ["in_group","buffer","out_group"]

class BufferItem(DictItem):
    
    def __init__(self,in_group,buffer,out_group):
        dict = {"in_group" : in_group,
                "buffer" : buffer,
                "out_group" : out_group}
        super().__init__(dict)
        
    def equals(self,other):
        return (self.dict == other.dict)
        
    def applyItem(self):
        debug("applyBuffer")
        in_group = self.dict["in_group"]
        in_group_item = groups.groupsModel.getGroupByName(in_group)
        in_layer = in_group_item.layer
        if not in_layer:
            in_group_item.instantiateLayer()
            in_layer = in_group_item.layer
            #in_layer = in_group_item.layer
        out_group = self.dict["out_group"]
        out_group_item = groups.groupsModel.getGroupByName(out_group)
        #out_layer = out_group_item.getLayer()
        if not out_group_item.layer:
            out_group_item.instantiateLayer(inLayer=in_layer,geomType="Polygon")
        #out_layer = createLayerFromExisting(in_layer,out_group,geomType="Polygon")
        out_layer = applyBuffer(in_layer,200,out_group_item.layer)
        assert (out_layer != None)
        out_group_item.layer = out_layer
        if not out_group_item.is_memory:
            out_group_item.saveLayerAsFile()
        #info(str(type(grp)))
        
        
class BufferModel(DictModel):
    
    def __init__(self):
        super().__init__(self,buffer_fields)
        
    @staticmethod
    def mkItemFromDict(dict):
        checkFields(buffer_fields,dict.keys())
        item = BufferItem(dict["in_layer"],dict["expr"],dict["group"])
        return item
        
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
        self.dlg.bufferRun.clicked.connect(self.model.applyItems)
        
    def mkItem(self):
        in_group = self.dlg.bufferInGroup.currentText()
        buffer_val = self.dlg.bufferValue.value()
        out_group = self.dlg.bufferOutGroup.currentText()
        bufferItem = BufferItem(in_group,buffer_val,out_group)
        return bufferItem