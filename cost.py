
import processing

import utils
import params
from .qgsUtils import *
import sous_trames
from .abstract_model import *
from .qgsTreatments import *

cost_fields = ["start_layer","perm_layer","cost"]

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
        utils.debug("Start runCost")
        st_name = self.dict["st_name"]
        st_item = sous_trames.getSTByName(st_name)
        startLayer = self.dict["start_layer"]
        utils.checkFileExists(startLayer)
        params.checkInit()
        extent_layer_path = params.getExtentLayer()
        #extent_layer_path = pathOfLayer(extent_layer)
        applyRasterization(startLayer,"geom",st_item.getStartLayerPath(),
                           params.getResolution(),extent_layer_path)
        permRaster = self.dict["perm_layer"]
        #utils.checkFileExists(permRaster)
        cost = self.dict["cost"]
        outPath = st_item.getDispersionPath(cost)#.replace("\\\\","/")
        applyRCost(startLayer,permRaster,cost,outPath)
        #outPath = 'D:\MChailloux\tmp\workspace\tmp2\tmp\st1_dispersion_200.tif'
        # debug ("startLayer = " + startLayer)
        # parameters = { 'input' : permRaster,
                        # 'start_raster' : startLayer,
                        # 'max_cost' : int(cost),
                        # 'output' : outPath,
                        # 'start_coordinates' : '0,0',
                        # 'stop_coordinates' : '0,0',
                        # 'outdir' : 'D:\MChailloux\PNRHL_QGIS\tmpLayer_movements.tif',
                        # 'nearest' : 'D:\MChailloux\PNRHL_QGIS\tmpLayer_nearest.tif',
                        # 'start_points' :  None,
                        # 'stop_points' : None,
                        # 'null_cost' : None,
                        # 'memory' : 5000,
                        # 'GRASS_REGION_CELLSIZE_PARAMETER' : 50,
                        # 'GRASS_SNAP_TOLERANCE_PARAMETER' : -1,
                        # 'GRASS_MIN_AREA_PARAMETER' : 0,
                        # '-k' : False,
                        # '-n' : False,
                        # '-r' : True,
                        # '-i' : False,
                        # '-b' : False}
        # utils.debug("parameters : " + str(parameters))
        # try:
            # processing.run("grass7:r.cost",parameters)
            # print ("call to r.cost successful")
        # except Exception as e:
            # print ("Failed to call r.cost : " + str(e))
            # raise e
        # finally:  
            # utils.debug("End runCost")
            
    def checkItem(self):
        pass
        
class CostModel(DictModel):
    
    def __init__(self):
        super().__init__(self,cost_fields)
    
    @staticmethod
    def mkItemFromDict(dict):
        utils.checkFields(cost_fields,dict.keys())
        item = CostItem(dict["st_name"],dict["start_layer"],dict["perm_layer"],dict["cost"])
        return item
        
        
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
        self.dlg.costStartLayerCombo.setFilters(QgsMapLayerProxyModel.VectorLayer)
        self.dlg.costPermRasterCombo.setFilters(QgsMapLayerProxyModel.RasterLayer)
        #self.dlg.rasterView.resize(self.dlg.width / 1.5, self.dlg.height / 3.5)
        
    def connectComponents(self):
        self.dlg.costSTCombo.setModel(sous_trames.stModel)
        self.dlg.costStartLayerCombo.layerChanged.connect(self.setStartLayerFromCombo)
        self.dlg.costPermRasterCombo.layerChanged.connect(self.setPermRasterFromCombo)
        self.dlg.costRun.clicked.connect(self.model.applyItems)
        super().connectComponents()
        
    def switchST(self,text):
        st_item = sous_trames.getSTByName(text)
        st_friction_path = st_item.getFrictionPath()
        self.dlg.costPermRaster.lineEdit().setValue(st_friction_path)
        
    def setStartLayerFromCombo(self,layer):
        utils.debug("setStartLayerFromCombo")
        if layer:
            path=pathOfLayer(layer)
            self.dlg.costStartLayer.lineEdit().setValue(path)
        
    def setPermRasterFromCombo(self,layer):
        utils.debug("setPermRasterFromCombo")
        if layer:
            path=pathOfLayer(layer)
            self.dlg.costPermRaster.lineEdit().setValue(path)
        
    def mkItem(self):
        st_name = self.dlg.costSTCombo.currentText()
        start_layer = self.dlg.costStartLayer.filePath()
        perm_layer = self.dlg.costPermRaster.filePath()
        cost = str(self.dlg.costMaxVal.value())
        cost_item = CostItem(st_name,start_layer,perm_layer,cost)
        return cost_item
        