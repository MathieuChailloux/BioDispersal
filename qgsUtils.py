
from qgis.gui import *
from qgis.core import *
from .utils import *

def writeShapefile(layer,outfname):
    crs = QgsCoordinateReferenceSystem("EPSG:2154")
    #params = 
    (error, error_msg) = QgsVectorFileWriter.writeAsVectorFormat(layer,outfname,'utf-8',destCRS=crs,driverName='ESRI Shapefile')
    if error == QgsVectorFileWriter.NoError:
        info("Shapefile '" + outfname + "' succesfully created")
    else:
        user_error("Unable to create shapefile '" + outfname + "' : " + str(error_msg))