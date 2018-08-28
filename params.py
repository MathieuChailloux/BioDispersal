
import os.path
import pathlib

from qgis.core import QgsCoordinateReferenceSystem, QgsRectangle
from qgis.gui import QgsFileWidget
from PyQt5.QtCore import QVariant, QAbstractTableModel, QModelIndex, Qt
from PyQt5.QtWidgets import QAbstractItemView, QFileDialog, QHeaderView

import utils
import qgsUtils
import qgsTreatments
import abstract_model


params = None

params_fields = ["extent","workspace","useRelPath","projectFile","crs"]

defaultCrs = QgsCoordinateReferenceSystem("EPSG:2154")

def checkWorkspaceInit():
    if not params.workspace:
        utils.user_error("Workspace parameter not initialized")
    if not os.path.isdir(params.workspace):
        utils.user_error("Workspace directory '" + params.workspace + "' does not exist")
        

def normalizePath(path):
    checkWorkspaceInit()
    if not path:
        utils.user_error("Empty path")
    pp = pathlib.Path(path)
    utils.debug("path = " + str(path))
    utils.debug("pp_str = " + str(pp))
    path = str(pp)
    if os.path.isabs(path):
        return os.path.relpath(path,params.workspace)
    else:
        return path
        
def getOrigPath(path):
    checkWorkspaceInit()
    if path == "":
        utils.user_error("Empty path")
    elif os.path.isabs(path):
        return path
    else:
        return os.path.normpath(os.path.join(params.workspace,path))
    
def checkInit():
    checkWorkspaceInit()
    if not params.extentLayer:
        utils.user_error("Extent layer paramter not initialized")
    utils.checkFileExists(getOrigPath(params.extentLayer),"Extent layer ")
    if not params.resolution:
        utils.user_error("Resolution paramter not initialized")
    if not params.crs:
        utils.user_error("CRS paramter not initialized")
    if not params.crs.isValid():
        utils.user_error("Invalid CRS")

def getPathFromLayerCombo(combo):
    layer = combo.currentLayer()
    layer_path = normalizePath(qgsUtils.pathOfLayer(layer))
    return layer_path
        
def getResolution():
    return params.resolution
    
def getExtentLayer():
    return getOrigPath(params.extentLayer)
    
def getExtentCoords():
    extent_path = getOrigPath(params.extentLayer)
    if extent_path:
        return qgsUtils.coordsOfExtentPath(extent_path)
    else:
        utils.user_error("Extent layer not initialized")
        
def equalsParamsExtent(path):
    params_coords = getExtentCoords()
    path_coords = qgsUtils.coordsOfExtentPath(path)
    return (params_coords == path_coords)
        
def getExtentRectangle():
    coords = getExtentCoords()
    rect = QgsRectangle(float(coords[0]),float(coords[1]),
                        float(coords[2]),float(coords[3]))
    return rect
    
def normalizeRaster(path,resampling_mode="near"):
    if equalsParamsExtent(path):
        return path
    else:
        #if not new_path:
        utils.debug("Diff coords : '" + str(getExtentCoords())
               + "' vs '" + str(qgsUtils.coordsOfExtentPath(path)))
        new_path = utils.mkTmpPath(path)
        crs = params.crs
        resolution = getResolution()
        extent_path = getExtentLayer()
        qgsTreatments.applyWarpGdal(path,new_path,resampling_mode,crs,resolution,extent_path)
        return new_path
        
def openFileDialog(parent,msg="",filter=""):
    checkWorkspaceInit()
    fname, filter = QFileDialog.getOpenFileName(parent,
                                                caption=msg,
                                                directory=params.workspace,
                                                filter=filter)
    return fname
    
def saveFileDialog(parent,msg="",filter=""):
    checkWorkspaceInit()
    fname, filter = QFileDialog.getSaveFileName(parent,
                                                caption=msg,
                                                directory=params.workspace,
                                                filter=filter)
    return fname
        
#class ParamsModel(abstract_model.AbstractGroupModel):
class ParamsModel(QAbstractTableModel):

    def __init__(self):
        self.workspace = None
        self.extentLayer = None
        self.resolution = None
        self.useRelativePath = True
        self.projectFile = ""
        self.crs = defaultCrs
        self.fields = ["workspace","extentLayer","resolution","projectFile","crs"]
        QAbstractTableModel.__init__(self)
        
    def setExtentLayer(self,path):
        path = normalizePath(path)
        self.extentLayer = path
        self.layoutChanged.emit()
        
    def setResolution(self,resolution):
        self.resolution = resolution
        self.layoutChanged.emit()
        
    def setCrs(self,crs):
        self.crs = crs
        self.layoutChanged.emit()
        
    def getCrsStr(self):
        return self.crs.authid().lower()
        
    def setWorkspace(self,path):
        self.workspace = path
        utils.info("Workspace directory set to '" + path)
        if not os.path.isdir(path):
            utils.user_error("Directory '" + path + "' does not exist")
        #self.tmpDir = os.path.join(path,"tmp")
            
    def setUseRelPath(self,state):
        if state:
            self.useRelativePath = True
        else:
            self.useRelativePath = False
        self.layoutChanged.emit()
    
    def fromXMLRoot(self,root):
        dict = root.attrib
        return self.fromXMLDict(dict)
    
    def fromXMLDict(self,dict):
        if "workspace" in dict:
            if os.path.isdir(dict["workspace"]):
                self.setWorkspace(dict["workspace"])
        if "extent" in dict:
            self.setExtentLayer(dict["extent"])
        if "resolution" in dict:
            self.setResolution(dict["resolution"])
        if "useRelPath" in dict:
            self.useRelativePath = bool(dict["useRelPath"])
        self.layoutChanged.emit()
    
    def toXML(self,indent=""):
        xmlStr = indent + "<ParamsModel"
        if self.workspace:
            xmlStr += " workspace=\"" + str(self.workspace) + "\""
        if self.resolution:
            xmlStr += " resolution=\"" + str(self.resolution) + "\""
        if self.extentLayer:
            xmlStr += " extent=\"" + str(self.extentLayer) + "\""
        if self.useRelativePath:
            xmlStr += " useRelPath=\"" + str(self.useRelativePath) + "\""
        xmlStr += "/>"
        return xmlStr
        
    def rowCount(self,parent=QModelIndex()):
        return len(self.fields)
        
    def columnCount(self,parent=QModelIndex()):
        return 1
              
    def getNItem(self,n):
        items = [self.workspace,
                 self.extentLayer,
                 self.resolution,
                 self.projectFile,
                 self.crs.description(),
                 ""]
        return items[n]
            
    def data(self,index,role):
        if not index.isValid():
            return QVariant()
        row = index.row()
        item = self.getNItem(row)
        if role != Qt.DisplayRole:
            return QVariant()
        elif row < self.rowCount():
            return(QVariant(item))
        else:
            return QVariant()
            
    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable
        
    def headerData(self,col,orientation,role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant("value")
        elif orientation == Qt.Vertical and role == Qt.DisplayRole:
            return QVariant(self.fields[col])
        return QVariant()

class ParamsConnector:

    def __init__(self,dlg):
        self.dlg = dlg
        self.model = ParamsModel()
        
    def initGui(self):
        #self.dlg.paramsView.setHorizontalScrollBarMode(QAbstractItemView.ScrollPerPixel)
        self.dlg.paramsView.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.dlg.extentLayer.setFilter("*.shp;*.tif")
        self.dlg.paramsCrs.setCrs(defaultCrs)
        self.model.setResolution(25)
        self.dlg.rasterResolution.setValue(25)
        
    def connectComponents(self):
        self.dlg.paramsView.setModel(self.model)
        self.dlg.rasterResolution.valueChanged.connect(self.model.setResolution)
        self.dlg.extentLayer.setStorageMode(QgsFileWidget.GetFile)
        self.dlg.extentLayer.fileChanged.connect(self.model.setExtentLayer)
        self.dlg.workspace.setStorageMode(QgsFileWidget.GetDirectory)
        self.dlg.workspace.fileChanged.connect(self.model.setWorkspace)
        self.dlg.paramsCrs.crsChanged.connect(self.model.setCrs)
        header = self.dlg.paramsView.horizontalHeader()     
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        self.model.layoutChanged.emit()
        
    
def normPath(p):
    if params.useRelativePath:
        return os.path.relpath(p,params.workspace)
    else:
        return p
        