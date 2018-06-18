
import processing

from params import *
from .utils import *
from .qgsUtils import *
import sous_trames
from .abstract_model import *

cost_fields = ["start_layer","perm_layer","cost","output_path"]

class CostItem(DictItem):

    def __init__(self,st_name,start_layer,perm_layer,cost):
        dict = {"st_name" : st_name,
                "start_layer" : start_layer,
                "perm_layer" : perm_layer,
                "cost" : cost}
        super().__init__(dict)
        
    def equals(self,other):
        if self.dict["st_name"] == other.dict["st_name"]:
            return False
        elif self.dict["cost"] == other.dict["cost"]:
            return False
        
    def applyItem(self):
        debug("Start runCost")
        checkInit()
        st_name = self.dict["st_name"]
        st_item = sous_trames.getSTByName(st_name)
        startRaster = self.dict["start_layer"]
        checkFileExists(startRaster)
        permRaster = self.dict["perm_layer"]
        checkFileExists(permRaster)
        cost = self.dict["cost"]
        outPath = st_item.getDispersionPath(cost)#.replace("\\\\","/")
        #outPath = 'D:\MChailloux\tmp\workspace\tmp2\tmp\st1_dispersion_200.tif'
        debug ("startRaster = " + startRaster)
        parameters = { 'input' : permRaster,
                        'start_raster' : startRaster,
                        'max_cost' : int(cost),
                        'output' : outPath,
                        #'start_coordinates' : '0,0',
                        #'stop_coordinates' : '0,0',
                        #'outdir' : 'D:\MChailloux\PNRHL_QGIS\tmpLayer_movements.tif',
                        #'nearest' : 'D:\MChailloux\PNRHL_QGIS\tmpLayer_nearest.tif',
                        #'start_points' :  None,
                        #'stop_points' : None,
                        'null_cost' : None,
                        'memory' : 5000,
                        'GRASS_REGION_CELLSIZE_PARAMETER' : 50,
                        'GRASS_SNAP_TOLERANCE_PARAMETER' : -1,
                        'GRASS_MIN_AREA_PARAMETER' : 0,
                        '-k' : False,
                        '-n' : False,
                        '-r' : True,
                        '-i' : False,
                        '-b' : False}
        debug("parameters : " + str(parameters))
        try:
            processing.run("grass7:r.cost",parameters)
            print ("call to r.cost successful")
        except Exception as e:
            print ("Failed to call r.cost : " + str(e))
            raise e
        finally:  
            debug("End runCost")
            
    def checkItem(self):
        pass
        
class CostModel(DictModel):
    
    def __init__(self):
        super().__init__(self,cost_fields)
        
    def fromXMLRoot(self,root):
        pass
        
class CostConnector(AbstractConnector):

    def __init__(self,dlg):
        self.dlg = dlg
        costModel = CostModel()
        super().__init__(costModel,self.dlg.costView,
                         self.dlg.costAdd,self.dlg.costRemove)
        #test_item = 
        #self.raster_model.
        
    def initGui(self):
        pass
        #self.dlg.rasterView.resize(self.dlg.width / 1.5, self.dlg.height / 3.5)
        
    def connectComponents(self):
        self.dlg.costSTCombo.setModel(sous_trames.stModel)
        self.dlg.costStartRasterCombo.layerChanged.connect(self.setStartRasterFromCombo)
        self.dlg.costPermRasterCombo.layerChanged.connect(self.setPermRasterFromCombo)
        self.dlg.costRun.clicked.connect(self.model.applyItems)
        super().connectComponents()
        
    def setStartRasterFromCombo(self,layer):
        debug("setStartRasterFromCombo")
        if layer:
            path=pathOfLayer(layer)
            self.dlg.costStartRaster.lineEdit().setValue(path)
        
    def setPermRasterFromCombo(self,layer):
        debug("setPermRasterFromCombo")
        if layer:
            path=pathOfLayer(layer)
            self.dlg.costPermRaster.lineEdit().setValue(path)
        
    def mkItem(self):
        st_name = self.dlg.costSTCombo.currentText()
        start_layer = self.dlg.costStartRaster.filePath()
        perm_layer = self.dlg.costPermRaster.filePath()
        cost = str(self.dlg.costMaxVal.value())
        cost_item = CostItem(st_name,start_layer,perm_layer,cost)
        return cost_item
        