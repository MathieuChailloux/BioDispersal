
from .utils import *
import params

ponderation_fields = ["in_layer","mode","out_layer","ponderation"]

pond_ival_fields = ["low_bound","up_bound","pond_value"]

class PondIvalModel(abstract_model.DictItem):
    
    def __init__(self):
        dict = {"low_bound": 0,
                "up_bound" : 0,
                "pond_value" : 1}

class PonderationItem(abstract_model.DictItem):
    
    def __init__(self,dict):
        super().__init__(dict)
        
    def applyItem(self):
        mode = self.dict["mode"]
        if mode == "Direct":
            self.applyItemDirect()
        elif mode == "Intervalles":
            self.applyIntervals()
        elif mode == "Tampon":
            self.applyBuffer()
        else:
            user_error("Unexpect ponderation mode '" + str(mode) + "'")
            
    def applyItemDirect(self):
        in_layer_path = self.dict["in_layer"]
        checkFileExists(in_layer_path)
        out_layer_path = self.dict["out_layer"]
        tmp_path = os.path.splitext(out_layer_path)[0] + "_tmp.tif"
        crs = params.params.crs
        resolution = params.getResolution()
        extent_path = params.getExtentLayer()
        applyWarpGdal(in_layer_path,tmp_path,"bilinear",crs,resolution,extent_path)
        applyPonderationGdal(in_layer_path,tmp_path,out_layer_path)
        os.remove(tmp_path)
        
    def applyItemIntervals(self):
        # TODO
        assert(False)
        
    def applyItemBuffer(self):
        # TODO
        assert(False)
        

class PonderationModel(DictModel):

    def __init__(self):
        super().__init__(self,ponderation_fields)
        
    @staticmethod
    def mkItemFromDict(dict):
        checkFields(selection_fields,dict.keys())
        item = SelectionItem(dict["in_layer"],dict["mode"],dict["out_layer"],dict["ponderation"])
        return item
        
        
class PonderationConnector(AbstractConnector):

    def __init__(self,dlg):
        self.dlg = dlg
        ponderationModel = PonderationModel()
        super().__init__(ponderationModel,self.dlg.ponderationView,
                        self.dlg.pondAdd,self.dlg.pondRemove)
        
        
    def initGui(self):
        plusIcon = QIcon(':plugins/eco_cont/icons/plus.png')
        minusIcon = QIcon(':plugins/eco_cont/icons/minus.png')
        self.dlg.pondClassPlus.setIcon(plusIcon)
        self.dlg.pondClassMinus.setIcon(minusIcon)
        self.activateDirectMode()
        
    def connectComponents(self):
        super().connectComponents()
        self.dlg.pondRun.connect(self.model.applyItems)
    
    def activateDirectMode(self):
        self.dlg.pondBufferFrame.hide()
        self.dlg.pondIvalFrame.hide()
        self.dlg.pondPondLabel.hide()
        
    def activateIvalMode(self):
        self.dlg.pondBufferFrame.hide()
        self.dlg.pondIvalFrame.show()
        self.dlg.pondPondLabel.show()
        
    def activateBufferMode(self):
        self.dlg.pondBufferFrame.hide()
        self.dlg.pondIvalFrame.show()
        self.dlg.pondPondLabel.show()
    
    
    
    