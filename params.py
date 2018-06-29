
import os.path

from qgis.core import QgsCoordinateReferenceSystem
from qgis.gui import QgsFileWidget
from PyQt5.QtCore import QVariant, QAbstractTableModel, QModelIndex, Qt
from PyQt5.QtWidgets import QAbstractItemView

import utils
import qgsUtils
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
    if os.path.isabs(path):
        return os.path.relpath(path,params.workspace)
    else:
        return path
        
def getOrigPath(path):
    checkWorkspaceInit()
    if os.path.isabs(path):
        return path
    else:
        return os.path.normpath(os.path.join(params.workspace,path))
    
def checkInit():
    checkWorkspaceInit()
    if not params.extentLayer:
        utils.user_error("Extent layer paramter not initialized")
    if not params.resolution:
        utils.user_error("Resolution paramter not initialized")
    if not params.crs:
        utils.user_error("CRS paramter not initialized")
    if not params.crs.isValid():
        utils.user_error("Invalid CRS")

def mkTmpPath(fname,abs_flag=False):
    if abs_flag:
        if params.tmpDir:
            tmpFname = os.path.join(params.tmpDir,fname)
            return tmpFname
        else:
            utils.user_error("Workspace not set")
    else:
        os.path.join("tmp",fname)
        
def getResolution():
    return params.resolution
    
def getExtentLayer():
    return getOrigPath(params.extentLayer)
    
def getExtentCoords():
    extent_path = getOrigPath(params.extentLayer)
    if extent_path:
        return qgsUtils.coordsOfExtentPath(extent_path)
        # extent_layer = qgsUtils.loadVectorLayer(extent_path)
        # extent = extent_layer.extent()
        # x_min = extent.xMinimum()
        # x_max = extent.xMaximum()
        # y_min = extent.yMinimum()
        # y_max = extent.yMaximum()
        # return [str(x_min),str(y_min),str(x_max),str(y_max)]
    else:
        utils.user_error("Extent layer not initialized")
        
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
        
        #self.extentLayerPath = path
        #self.extentLayer = qgsUtils.loadVectorLayer(self.extentLayerPath)
        
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
        utils.debug("Workspace directory set to '" + path)
        if not os.path.isdir(path):
            utils.user_error("Directory '" + path + "' does not exist")
        self.tmpDir = os.path.join(path,"tmp")
        if not os.path.isdir(self.tmpDir):
            os.makedirs(self.tmpDir)
            utils.debug("Temporary directory '" + self.tmpDir + "' created")
            
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
        self.dlg.extentLayer.setFilter("*.shp")
        self.dlg.saveModelPath.setFilter("*.xml")
        self.dlg.loadModelPath.setFilter("*.xml")
        self.dlg.paramsCrs.setCrs(defaultCrs)
        self.dlg.options2Frame.hide()
        self.model.setResolution(25)
        self.dlg.rasterResolution.setValue(25)
        #self.dlg.loadModelFrame.hide()
        
    def connectComponents(self):
        self.dlg.paramsView.setModel(self.model)
        self.dlg.rasterResolution.valueChanged.connect(self.model.setResolution)
        self.dlg.extentLayer.setStorageMode(QgsFileWidget.GetFile)
        self.dlg.extentLayer.fileChanged.connect(self.model.setExtentLayer)
        self.dlg.workspace.setStorageMode(QgsFileWidget.GetDirectory)
        self.dlg.workspace.fileChanged.connect(self.model.setWorkspace)
        self.dlg.paramsRelPath.stateChanged.connect(self.model.setUseRelPath)
        self.dlg.paramsCrs.crsChanged.connect(self.model.setCrs)
        self.model.layoutChanged.emit()
        
        
# def initParams(dlg):
    # global params
    # paramsModel = ParamsConnector()
    
def normPath(p):
    if params.useRelativePath:
        return os.path.relpath(p,params.workspace)
    else:
        return p
        