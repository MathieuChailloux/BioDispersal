
from .abstract_model import AbstractGroupModel, AbstractGroupItem, DictItem, DictModel, AbstractConnector
from .utils import *
from .qgsUtils import *
#from .groups import classModel
import classes

selection_fields = ["in_layer","expr","class"]

# TODO : manage duplicates
class SelectionItem(DictItem):

    def __init__(self,in_layer,expr,group):
        dict = {"in_layer" : in_layer,
                "expr" : expr,
                "class" : group}
        self.is_vector = isVectorPath(in_layer)
        self.is_raster = isRasterPath(in_layer)
        cls = classes.classModel.getClassByName(group)
        if not cls:
            cls = classes.ClassItem(group,"")
            classes.classModel.addItem(cls)
        self.cls = cls
        super().__init__(dict)
        
    def checkParams(self):
        pass
        
    def applyItem(self):
        if self.is_vector:
            self.applyVectorItem()
        elif self.is_raster:
            self.applyRasterItem()
        else:
            user_error("Unkown format for file '" + str(self.dict["in_layer"]))
        
    def applyItemVector(self):
        debug("classModel = " + str(classes.classModel))
        in_layer_path = self.dict["in_layer"]
        checkFileExists(in_layer_path)
        in_layer = loadVectorLayer(in_layer_path)
        expr = self.dict["expr"]
        class_name = self.dict["class"]
        class_item = classes.classModel.getClassByName(class_name)
        out_vector_layer = class_item.vectorLayer
        if not out_vector_layer:
            out_vector_layer = createLayerFromExisting(in_layer,class_name + "_vector")
            #class_item.vector_layer = out_vector_layer
            pr = out_vector_layer.dataProvider()
            orig_field = QgsField("Origin", QVariant.String)
            pr.addAttributes([orig_field])
            out_vector_layer.updateFields()
        if expr:
            feats = in_layer.getFeatures(QgsFeatureRequest().setFilterExpression(expr))
        else:
            feats = in_layer.getFeatures(QgsFeatureRequest())
        fields = out_vector_layer.fields()
        new_f = QgsFeature(new_fields)
        tmp_cpt = 0
        for f in feats:
            tmp_cpt += 1
            new_f.setGeometry(f.geometry())
            new_f["Origin"] = in_layer.name()
            res = pr.addFeature(new_f)
            if not res:
                internal_error("ko")
            out_layer.updateExtents()
        debug("length(feats) = " + str(tmp_cpt))
        if tmp_cpt == 0:
            warn("No entity selected from '" + str(self) + "'")
        class_item.saveVectorLayer()
            
    def applyItemRaster(self):
        internal_error("[applyItemRaster]")
        
class SelectionModel(DictModel):
    
    def __init__(self):
        super().__init__(self,selection_fields)
        
    @staticmethod
    def mkItemFromDict(dict):
        checkFields(selection_fields,dict.keys())
        item = RasterItem(dict["in_layer"],dict["expr"],dict["class"])
        return item

class SelectionConnector(AbstractConnector):

    def __init__(self,dlg,classModel):
        self.dlg = dlg
        selectionModel = SelectionModel()
        self.classModel = classModel
        super().__init__(selectionModel,self.dlg.selectionView,
                        self.dlg.selectionAdd,self.dlg.selectionRemove)
                        
    def initGui(self):
        pass
        
    def connectComponents(self):
        super().connectComponents()
        self.dlg.selectionInLayerCombo.layerChanged.connect(self.setInLayerFromCombo)
        self.dlg.selectionInLayer.fileChanged.connect(self.setInLayer)
        self.dlg.selectionFieldLayerCombo.layerChanged.connect(self.setInLayerFieldFromCombo)
        self.dlg.selectionFieldLayer.fileChanged.connect(self.setInLayerField)
        self.dlg.selectionFieldAdd.clicked.connect(self.addItemsFromField)
        self.dlg.selectionGroupCombo.setModel(self.classModel)
        self.dlg.selectionRun.clicked.connect(self.model.applyItems)
                        
    def setInLayerFromCombo(self,layer):
        debug("setInLayerFromCombo")
        path=pathOfLayer(layer)
        self.dlg.selectionInLayer.lineEdit().setValue(path)
        self.dlg.selectionExpr.setLayer(layer)
        
    def setInLayer(self,path):
        debug("setInLayer " + path)
        loaded_layer = loadVectorLayer(path)
        debug(str(loaded_layer))
        if loaded_layer == None:
            user_error("Could not load layer '" + path + "'")
        if not loaded_layer.isValid():
            user_error("Invalid layer '" + path + "'")
        debug(str(loaded_layer.fields().names()))
        # TODO : fix setLayer not working
        self.dlg.selectionExpr.setLayer(loaded_layer)
        
    def setInLayerFieldFromCombo(self,layer):
        debug("[setInLayerFieldFromCombo]")
        path=pathOfLayer(layer)
        self.dlg.selectionFieldLayer.lineEdit().setValue(path)
        self.dlg.selectionField.setLayer(layer)
        
    def setInLayerField(self,path):
        debug("[setInLayerField]")
        #layer = loadVectorLayer(path)
        layer = QgsVectorLayer(path, "test", "ogr")
        # TODO : fix setLayer not working
        self.dlg.selectionField.setLayer(layer)
        
        
    def mkItem(self):
        in_layer = self.dlg.selectionInLayer.filePath()
        expr = self.dlg.selectionExpr.expression()
        group = self.dlg.selectionGroupCombo.currentText()
        selection = SelectionItem(in_layer,expr,group)
        return selection
        
    def mkItemsFromField(self):
        in_layer_path = self.dlg.selectionFieldLayer.filePath()
        in_layer = loadVectorLayer(in_layer_path)
        field_name = self.dlg.selectionField.currentField()
        field_values = set()
        for f in in_layer.getFeatures():
            field_values.add(f[field_name])
        debug(str(field_values))
        items = []
        for fv in field_values:
            expr = "\"" + field_name + "\" = " + str(fv)
            item = SelectionItem(in_layer_path,expr,fv)
            items.append(item)
        return items
        
    def addItemsFromField(self):
        debug("[addItemsFromField]")
        items = self.mkItemsFromField()
        for i in items:
            self.model.addItem(i)
        self.model.layoutChanged.emit()
    