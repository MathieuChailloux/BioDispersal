
import os.path

from qgis.gui import QgsFileWidget
from PyQt5.QtCore import QVariant, QAbstractTableModel, QModelIndex, Qt
from PyQt5.QtWidgets import QAbstractItemView

import utils
import qgsUtils
import abstract_model


params = None

params_fields = ["extent","workspace","useRelPath"]

def checkInit():
    if not params.workspace:
        utils.user_error("Workspace parameter not initialized")
    if not params.extentLayer:
        utils.user_error("Extent layer paramter not initialized")
    if not params.resolution:
        utils.user_error("Resolution paramter not initialized")

def mkTmpPath(fname):
    if params.tmpDir:
        tmpFname = os.path.join(params.tmpDir,fname)
        return tmpFname
    else:
        utils.user_error("Workspace not set")
        
def getResolution():
    return params.resolution
    
def getExtentLayer():
    return params.extentLayer
    
def getExtentCoords():
    extent_path = params.extentLayer
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
        self.fields = ["workspace","extentLayer","resolution"]
        QAbstractTableModel.__init__(self)
        
    def setExtentLayer(self,path):
        self.extentLayer = path
        self.layoutChanged.emit()
        
        #self.extentLayerPath = path
        #self.extentLayer = qgsUtils.loadVectorLayer(self.extentLayerPath)
        
    def setResolution(self,resolution):
        self.resolution = resolution
        self.layoutChanged.emit()
        
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
        ws = dict["workspace"]
        if ws:
            self.setWorkspace(ws)
        et = dict["extent"]
        if et:
            self.setExtentLayer(et)
        resolution = dict["resolution"]
        if resolution:
            self.setResolution(resolution)
        self.useRelativePath = bool(dict["useRelPath"])
        self.layoutChanged.emit()
    
    def toXML(self,indent=""):
        xmlStr = indent + "<ParamsModel"
        xmlStr += " resolution=\"" + str(self.resolution) + "\""
        xmlStr += " workspace=\"" + str(self.workspace) + "\""
        xmlStr += " extent=\"" + str(self.extentLayer) + "\""
        xmlStr += " useRelPath=\"" + str(self.useRelativePath) + "\""
        xmlStr += "/>"
        return xmlStr
        
    def rowCount(self,parent=QModelIndex()):
        return 3
        
    def columnCount(self,parent=QModelIndex()):
        return 1
              
    def getNItem(self,n):
        items = [self.workspace,
                 self.extentLayer,
                 self.resolution,
                 self.useRelativePath,
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
        #self.dlg.loadModelFrame.hide()
        
    def connectComponents(self):
        self.dlg.paramsView.setModel(self.model)
        self.dlg.rasterResolution.valueChanged.connect(self.model.setResolution)
        self.dlg.extentLayer.setStorageMode(QgsFileWidget.GetFile)
        self.dlg.extentLayer.fileChanged.connect(self.model.setExtentLayer)
        self.dlg.workspace.setStorageMode(QgsFileWidget.GetDirectory)
        self.dlg.workspace.fileChanged.connect(self.model.setWorkspace)
        self.dlg.paramsRelPath.stateChanged.connect(self.model.setUseRelPath)
        
        
# def initParams(dlg):
    # global params
    # paramsModel = ParamsConnector()
    
def normPath(p):
    if params.useRelativePath:
        return os.path.relpath(p,params.workspace)
    else:
        return p
        