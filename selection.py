
from .abstract_model import AbstractGroupModel, AbstractGroupItem, DictItem, DictModel, AbstractConnector
from .utils import *
from .qgsUtils import *
#from .groups import groupsModel
import groups

selection_fields = ["in_layer","expr","group"]

# TODO : manage duplicates
class SelectionItem(DictItem):

    def __init__(self,in_layer,expr,group):
        dict = {"in_layer" : in_layer,
                "expr" : expr,
                "group" : group}
        super().__init__(dict)
        
    def checkParams(self):
        pass
        
    def applyItem(self):
        debug("groupsModel = " + str(groups.groupsModel))
        in_layer_path = self.dict["in_layer"]
        checkFileExists(in_layer_path)
        in_layer = loadVectorLayer(in_layer_path)
        expr = self.dict["expr"]
        out_name = self.dict["group"]
        groupItem = groups.groupsModel.getGroupByName(out_name)
        group_layer = groupItem.getLayer()
        if not group_layer:
            group_layer = createLayerFromExisting(in_layer,out_name)
            out_storage = groupItem.dict["layer"]
            if out_storage != "memory":
                writeShapefile(group_layer,out_storage)
            pr = group_layer.dataProvider()
            #group_field = QgsField("Group", QVariant.String)
            orig_field = QgsField("Origin", QVariant.String)
            new_fields = QgsFields()
            #new_fields.append(group_field)
            new_fields.append(orig_field)
            #pr.addAttributes([group_field,orig_field])
            pr.addAttributes([orig_field])
            group_layer.updateFields()
            debug("fields = " + str(len(pr.fields())))
            #checkLayersCompatible(k_layer,s.in_layer)
        if expr:
            feats = in_layer.getFeatures(QgsFeatureRequest().setFilterExpression(expr))
        else:
            feats = in_layer.getFeatures(QgsFeatureRequest())
        #debug("length(feats) = " + str(len(feats)))
        new_f = QgsFeature(new_fields)
        tmp_cpt = 0
        for f in feats:
            tmp_cpt += 1
            new_f.setGeometry(f.geometry())
            #new_f["Group"] = s.group
            new_f["Origin"] = in_layer.name()
            res = pr.addFeature(new_f)
            if not res:
                internal_error("ko")
            group_layer.updateExtents()
        debug("length(feats) = " + str(tmp_cpt))
        if tmp_cpt == 0:
            warn("No entity selected from '" + str(self) + "'")
        if out_storage != "memory":
            writeShapefile(group_layer,out_storage)
        
class SelectionModel(DictModel):
    
    def __init__(self):
        super().__init__(self,selection_fields)
        
    @staticmethod
    def mkItemFromDict(dict):
        checkFields(selection_fields,dict.keys())
        item = RasterItem(dict["in_layer"],dict["expr"],dict["group"])
        return item

class SelectionConnector(AbstractConnector):

    def __init__(self,dlg,groupsModel):
        self.dlg = dlg
        self.selectionModel = SelectionModel()
        self.groupsModel = groupsModel
        super().__init__(self.selectionModel,self.dlg.selectionView,
                        self.dlg.selectionAdd,self.dlg.selectionRemove)
                        
    def initGui(self):
        pass
        
    def connectComponents(self):
        super().connectComponents()
        self.dlg.selectionInLayerCombo.layerChanged.connect(self.setInLayer)
        self.dlg.selectionGroupCombo.setModel(self.groupsModel)
        self.dlg.selectionRun.clicked.connect(self.model.applyItems)
                        
    def setInLayer(self,layer):
        debug("setInLayer")
        path=pathOfLayer(layer)
        self.dlg.selectionInLayer.lineEdit().setValue(path)
        self.dlg.selectionExpr.setLayer(layer)
        
    def mkItem(self):
        in_layer = self.dlg.selectionInLayer.filePath()
        expr = self.dlg.selectionExpr.expression()
        #group = self.dlg.selectionGroup.text()
        group = self.dlg.selectionGroupCombo.currentText()
        #metagroup = self.dlg.selectionMetagroup.text()
        #out_layer = self.dlg.selectionOutLayer.filePath()
        #if not out_layer:
        #    out_layer = "memory"
        selection = SelectionItem(in_layer,expr,group)
        return selection
        
# class SelectionConnector(AbstractConnector):

    # def __init__(self,dlg,groupsModel):
        # self.dlg = dlg
        # self.selectionModel = SelectionModel()
        # self.groupsModel = groupsModel
        
    # def initGui(self):
        # pass
        
    # def connectComponents(self):
        # self.dlg.selectionView.setModel(self.selectionModel)
        # self.dlg.selectionGroupComco.setModel(self.groupsModel)
        # self.dlg.selectionInLayerCombo.layerChanged.connect(self.setInLayer)
        
    # def setInLayer(self,layer):
        # path=layer.dataProvider().dataSourceUri()
        # self.dlg.selectionInLayer.lineEdit().setValue(path)
        
    # def addSelectionItem(self):
        # in_layer = self.dlg.selectionInLayer.filePath()
        # expr = self.dlg.selectionExpr.expression()
        # group = self.dlg.selectionGroup.text()
        # metagroup = self.dlg.selectionMetagroup.text()
        # out_layer = self.dlg.selectionOutLayer.filePath()
        # if not out_layer:
            # out_layer = "memory"
        # selection = SelectionItem(in_layer,expr,group,metagroup,out_layer)
        # self.selectionModel.addItem(selection)
        # self.selectionModel.layoutChanged.emit()
        
    # def removeSelectionItem(self):
    