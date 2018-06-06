
import os.path

from qgis.gui import QgsFileWidget

import utils
import qgsUtils

params = None

class ParamsModel:

    def __init__(self):
        self.extentLayer = None
        self.workspace = None
        self.useRelativePath = True
        
    def setExtentLayer(self,path):
        self.extentLayerPath = path
        self.extentLayer = qgsUtils.loadVectorLayer(self.extentLayerPath)
        
    def setWorkspace(self,path):
        self.workspace = path
        utils.debug("Workspace directory set to '" + path)
        self.tmpDir = os.path.join(path,"tmp")
        if not os.path.isdir(self.tmpDir):
            os.makedirs(self.tmpDir)
            utils.debug("Temporary directory '" + self.tmpDir + "' created")
            
    def setUseRelPath(self,state):
        if state:
            self.useRelativePath = True
        else:
            self.useRelativePath = False
    
    def toXML(self):
        return ""

class ParamsConnector:

    def __init__(self,dlg):
        self.dlg = dlg
        self.model = ParamsModel()
        
    def initGui(self):
        pass
        
    def connectComponents(self):
        self.dlg.extentLayer.setStorageMode(QgsFileWidget.GetFile)
        self.dlg.workspace.setStorageMode(QgsFileWidget.GetDirectory)
        self.dlg.extentLayer.fileChanged.connect(self.model.setExtentLayer)
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
        
def mkTmpPath(fname):
    if params.tmpDir:
        tmpFname = os.path.join(params.tmpDir,fname)
        return tmpFname
    else:
        utils.user_error("Workspace not set")