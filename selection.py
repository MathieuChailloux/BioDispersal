
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

    def __init__(self,dlg):
        self.dlg = dlg
        self.selectionModel = SelectionModel()
        
    def initGui(self):
        pass
        
    def connectComponents(self):
        self.dlg.selectionView.setModel(self.selectionModel)
        
    def addSelectionItem(self):
        in_layer = self.dlg.selectionInLayer.currentLayer()
        expr = self.dlg.selectionExpr.expression()
        group = self.dlg.selectionGroup.text()
        metagroup = self.dlg.selectionMetagroup.text()
        out_layer = self.dlg.selectionOutLayer.filePath()
        if not out_layer:
            out_layer = "memory"
        
     