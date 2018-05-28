

from .utils import *
from .qgsUtils import *

cost_fields = ["start_layer","perm_layer","cost","output_path"]

class CostItem(DictItem):

    def __init__(self,start_layer,perm_layer,cost,out_path):
        dict = {"start_layer" : start_layer;
                "perm_layer" : perm_layer,
                "cost" : cost,
                "output_path" : out_path}
        super().__init__(dict)
        
        
    def applyRCost(self):
        debug("Start runCost")
        startRaster = self.dict["start_layer"]
        permRaster = self.dict["perm_layer"]
        cost = self.dict["cost"]
        outPath = self.dict["output_path"]
        debug ("startRaster = " + startRaster.name())
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
        #parameters = {}
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
        
        
class Cost:

    def __init__(self,dlg):
        self.dlg = dlg
        self.cost_model = CostModel()
        #test_item = 
        #self.raster_model.
        
    def initGui(self):
        pass
        #self.dlg.rasterView.resize(self.dlg.width / 1.5, self.dlg.height / 3.5)
        
    def connectComponents(self):
        #self.dlg.rasterRun.clicked.connect(self.applyBuffer)
        self.dlg.rasterInLayer.layerChanged.connect(self.updateFieldLayer)
        self.dlg.rasterAdd.clicked.connect(self.addRasterItem)
        self.dlg.rasterRun.clicked.connect(self.rasterizeItems)
        self.dlg.rasterOutLayer.setStorageMode(QgsFileWidget.SaveFile)
        self.dlg.rasterView.setModel(self.raster_model)
        #self.dlg.rasterField.layerChanged.connect(self.setField)