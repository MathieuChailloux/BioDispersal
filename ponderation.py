
import re

from .utils import *
from .qgsTreatments import *
import params
import abstract_model

from PyQt5.QtGui import QIcon



ponderation_fields = ["mode","friction","ponderation","out_layer"]

pond_ival_fields = ["low_bound","up_bound","pond_value"]
pond_buffer_fields = [""]

float_re="\d+\.\d+"
ival_re = "\(\[(" + float_re + "),(" + float_re + ")\],(" + float_re + ")\)"

class PondIvalItem(abstract_model.DictItem):

    def __init__(self,lb=0.0,ub=0.0,pv=1.0):
        dict = {"low_bound": lb,
                "up_bound" : ub,
                "pond_value" : pv}
        super().__init__(dict)
        
    def __str__(self):
        s = "([" + str(self.dict["low_bound"]) + ","
        s += str(self.dict["up_bound"]) + "],"
        s += str(self.dict["pond_value"]) + ")"
        return s
        
    def toIvalStr(self):
        s = str(self.dict["low_bound"])+ " - " + str(self.dict["up_bound"])
        return s
        
    @classmethod
    def fromStr(cls,s):
        match = re.search(ival_re,s)
        if match:
            lb = match.group(1)
            ub = match.group(2)
            pv = match.group(3)
            return cls(lb,ub,pv)
        else:
            internal_error("No match for ponderation interval item in string '" + s + "'")
            
    def checkItem(self):
        if (self.dict["low_bound"] > self.dict["up_bound"]):
            utils.user_error("Ill-formed interval : " + str(self))
            
    def checkOverlap(self,other):
        if (self.dict["up_bound"] <= other.dict["low_bound"]):
            return -1
        elif (self.dict["low_bound"] >= other.dict["up_bound"]):
            return 1
        else:
            user_error("Overlapping intervals : " + str(self) + " vs " + str(other))
        
class PondValueIvalItem(PondIvalItem):

    def __init__(self,lb=0.0,ub=0.0,pv=1.0):
        super().__init__(lb,ub,pv)

    def toGdalCalcExpr(self):
        s = "(" + str(self.dict["pond_value"])
        s += "*A*less_equal(" + str(self.dict["low_bound"]) + ",A)"
        s += "*less(A," + str(self.dict["up_bound"]) + ")"
        return s
        # TODO : function in qgsTreatments
        
class PondBufferIvalItem(PondIvalItem):

    def __init__(self,lb=0.0,ub=0.0,pv=1.0):
        super().__init__(lb,ub,pv)

    def toGdalCalcExpr(self,idx):
        s = "(A=" + str(idx) + ")*" + str(self.dict["pond_value"])
        return s
        
        
class PondIvalModel(abstract_model.DictModel):
    
    def __init__(self):
        super().__init__(self,pond_ival_fields)
        
    def __str__(self):
        s = ""
        for i in self.items:
            if s != "":
                s += " - "
            s += str(i)
        return s
        
    def checkItems(i1,i2):
        if (i1.dict["up_bound"] <= i2.dict["low_bound"]):
            return -1
        elif (i1.dict["low_bound"] >= i2.dict["up_bound"]):
            return 1
        else:
            user_error("Overlapping intervals : " + str(i1) + " vs " + str(i2))
        
    def checkModel(self):
        n = len(self.items)
        for i1 in range(0,n):
            for i2 in range(i1+1,n):
                self.checkItems(i1,i2)
        
    def toGdalCalcExpr(self):
        s = ""
        for ival in self.items:
            if ival != "":
                s+= " + "
            s += ival.toGdalCalcExpr()
        return s
        
class PondValueIvalModel(PondIvalModel):

    def __init__(self):
        super().__init__()
        
    @classmethod
    def fromStr(cls,s):
        res = cls()
        ivals = str.split('-')
        for ival_str in ivals:
            ival = PondValueIvalItem.fromStr(ival_str.strip())
            res.addItem(ival)
        return res
        
class PondBufferIvalModel(PondIvalModel):

    def __init__(self):
        super().__init__()
        
    @classmethod
    def fromStr(cls,s):
        res = cls()
        ivals = str.split('-')
        for ival_str in ivals:
            ival = PondBufferIvalItem.fromStr(ival_str)
            res.addItem(ival)
        return res
        
        
class PondValueIvalConnector(abstract_model.AbstractConnector):
    
    def __init__(self,dlg):
        self.dlg = dlg
        pondIvalModel = PondValueIvalModel()
        super().__init__(pondIvalModel,self.dlg.pondIvalView,
                         self.dlg.pondIvalPlus,self.dlg.pondIvalMinus)
                         
    def initGUi(self):
        pass
        
    def connectComponents(self):
        super().connectComponents()
        
    def mkItem(self):
        item = PondValueIvalItem()
        return item
        
class PondBufferIvalConnector(abstract_model.AbstractConnector):
    
    def __init__(self,dlg):
        self.dlg = dlg
        pondBufferModel = PondBufferIvalModel()
        super().__init__(pondBufferModel,self.dlg.pondBufferView,
                         self.dlg.pondBufferPlus,self.dlg.pondBufferMinus)
                         
    def initGUi(self):
        pass
        
    def connectComponents(self):
        super().connectComponents()
        
    def mkItem(self):
        item = PondBufferIvalModel()
        return item
        
# class PondBufferItem(abstract_model.DictItem):

    # def __init__(self):
        # dict = {"low_bound": 0,
                # "up_bound" : 0,
                # "pond_value" : 1}
        # super().__init__(dict)
        

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
            user_error("Unexpected ponderation mode '" + str(mode) + "'")
            
    def applyPonderation(self,layer1,layer2,out_layer):
        checkFileExists(layer1)
        checkFileExists(layer2)
        layer2_norm = params.normalizeRaster(layer2)
        applyPonderationGdal(layer1,layer2_norm,out_layer)
            
    def applyItemDirect(self):
        friction_layer_path = self.dict["friction_layer"]
        ponderation_layer_path = self.dict["ponderation_layer"]
        out_layer_path = self.dict["out_layer"]
        self.applyPonderation(friction_layer_path,ponderation_layer_path,out_layer_path)
        
    def applyItemValueIvals(self):
        friction_layer_path = self.dict["friction_layer"]
        #ponderation_layer_path = self.dict["ponderation_layer"]
        out_layer_path = self.dict["out_layer"]
        expr = self.dict["ponderation"]
        checkFileExists(friction_layer_path)
        ival_model = PondValueIvalModel.fromStr(expr)
        gdalc_calc_expr = ival_model.toGdalCalcExpr()
        applyGdalCalc(friction_layer_path,out_layer_path)
        
        
    def applyItemBufferIvals(self):
        friction_layer_path = self.dict["friction_layer"]
        #ponderation_layer_path = self.dict["ponderation_layer"]
        out_layer_path = self.dict["out_layer"]
        expr = self.dict["ponderation"]
        checkFileExists(friction_layer_path)
        ival_model = PondBufferIvalModel.fromStr(expr)
        gdalc_calc_expr = ival_model.toGdalCalcExpr()
        applyGdalCalc(friction_layer_path,out_layer_path)
        

class PonderationModel(abstract_model.DictModel):

    def __init__(self):
        super().__init__(self,ponderation_fields)
        
    @staticmethod
    def mkItemFromDict(dict):
        checkFields(selection_fields,dict.keys())
        item = PonderationItem(dict)
        return item
        
    def mkItem(self):
        assert(False)
        
class PonderationConnector(abstract_model.AbstractConnector):

    def __init__(self,dlg):
        self.dlg = dlg
        ponderationModel = PonderationModel()
        super().__init__(ponderationModel,self.dlg.ponderationView,
                        self.dlg.pondAdd,self.dlg.pondRemove)
        
        
    def initGui(self):
        plusIcon = QIcon(':plugins/eco_cont/icons/plus.png')
        minusIcon = QIcon(':plugins/eco_cont/icons/minus.png')
        saveIcon = QIcon(':plugins/eco_cont/icons/save.png')
        deleteIcon = QIcon(':plugins/eco_cont/icons/delete.svg')
        runIcon = QIcon(':plugins/eco_cont/icons/play.svg')
        self.dlg.pondIvalPlus.setIcon(plusIcon)
        self.dlg.pondIvalPlus.setToolTip("Ajouter un nouvel intervalle")
        self.dlg.pondIvalMinus.setIcon(minusIcon)
        self.dlg.pondIvalMinus.setToolTip("Supprimer l'intervalle sélectionné")
        self.dlg.pondBufferPlus.setIcon(plusIcon)
        self.dlg.pondBufferPlus.setToolTip("Ajouter un nouvel intervalle")
        self.dlg.pondBufferMinus.setIcon(minusIcon)
        self.dlg.pondBufferMinus.setToolTip("Supprimer l'intervalle sélectionné")
        self.dlg.pondAdd.setIcon(saveIcon)
        self.dlg.pondRemove.setIcon(deleteIcon)
        self.dlg.pondRemove.setToolTip("Supprimer les pondérations sélectionnées")
        self.dlg.pondRun.setIcon(runIcon)
        self.dlg.pondModeCombo.addItem("Direct")
        self.dlg.pondModeCombo.addItem("Intervalles")
        self.dlg.pondModeCombo.addItem("Tampons")
        self.dlg.pondModeCombo.setCurrentText("Direct")
        self.activateDirectMode()
        
    def connectComponents(self):
        super().connectComponents()
        self.dlg.pondRun.clicked.connect(self.model.applyItems)
        self.valueConnector = PondValueIvalConnector(self.dlg)
        self.valueConnector.connectComponents()
        self.bufferConnector = PondBufferIvalConnector(self.dlg)
        self.bufferConnector.connectComponents()
        self.dlg.pondModeCombo.currentTextChanged.connect(self.switchPondMode)
    
    def mkItem(self):
        mode = self.dlg.pondModeCombo.currentText()
        if not mode:
            utils.user_error("No ponderation mode selected")
        friction_layer_path = params.getPathFromLayerCombo(self.dlg.pondFrictLayerCombo)
        out_path = self.dlg.pondOutLayer.filePath()
        if mode == "Direct":
            pond =  params.getPathFromLayerCombo(self.dlg.pondDirectLayerCombo)
        elif mode == "Intervalles":
            pond = str(self.valueConnector.model)
        elif mode == "Tampons":
            pond = str(self.bufferConnector.model)
        else:
            internal_error("Unexpected ponderation mode '" + str(mode) + "'")
        item = PonderationItem(mode,friction_layer_path,pond,out_path)
        return item
    
    def switchPondMode(self,mode):
        if mode == "Direct":
            self.activateDirectMode()
        elif mode == "Intervalles":
            self.activateIvalMode()
        elif mode == "Tampons":
            self.activateBufferMode()
        else:
            internal_error("Unexpected ponderation mode '" + str(mode) + "'")
        
    
    def activateDirectMode(self):
        debug("activateDirectMode")
        self.dlg.pondDirectFrame.show()
        self.dlg.pondBufferFrame.hide()
        self.dlg.pondIvalFrame.hide()
        
    def activateIvalMode(self):
        debug("activateIvalMode")
        self.dlg.pondIvalFrame.show()
        self.dlg.pondBufferFrame.hide()
        self.dlg.pondDirectFrame.hide()
        
    def activateBufferMode(self):
        debug("activateBufferMode")
        self.dlg.pondBufferFrame.show()
        self.dlg.pondIvalFrame.hide()
        self.dlg.pondDirectFrame.hide()
    
    
    
    