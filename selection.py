
selection_fields = ["in_layer","expr","group"]

class SelectionItem(DictItem):

    def __init__(self,in_layer,expr,group,metagroup,out_layer):
        if not metagroup
            metagroup = "dummy"
        dict = {"in_layer" : in_layer,
                "expr" : expr,
                "group" : group,
                "out_layer" : out_layer}
        super().__init__(dict)
        
        
    def checkParams(self):
        pass
        
class SelectionModel(DictModel):
    
    def __init__(self):
        super().__init__(self,raster_displayed_fields)
        

class Selections:

    def __init__(self,dlg,groupsModel):
        self.dlg = dlg
        self.selectionModel = SelectionModel()
        self.groupsModel = groupsModel
        
    def initGui(self):
        pass
        
    def connectComponents(self):
        self.dlg.selectionView.setModel(self.selectionModel)
        self.dlg.selectionGroupComco.setModel(self.groupsModel)
        self.dlg.selectionInLayerCombo.layerChanged.connect(self.setInLayer)
        
    def setInLayer(self,layer):
        path=layer.dataProvider().dataSourceUri()
        self.dlg.selectionInLayer.lineEdit().setValue(path)
        
    def addSelectionItem(self):
        in_layer = self.dlg.selectionInLayer.filePath()
        expr = self.dlg.selectionExpr.expression()
        group = self.dlg.selectionGroup.text()
        metagroup = self.dlg.selectionMetagroup.text()
        out_layer = self.dlg.selectionOutLayer.filePath()
        if not out_layer:
            out_layer = "memory"
        selection = SelectionItem(in_layer,expr,group,metagroup,out_layer)
        self.selectionModel.addItem(selection)
        self.selectionModel.layoutChanged.emit()
        
    def removeSelectionItem(self):
    