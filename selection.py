
from .abstract_model import AbstractGroupModel, AbstractGroupItem, DictItem, DictModel, AbstractConnector
from .utils import *
from .qgsUtils import *
#from .groups import classModel
import classes
import groups
from .qgsTreatments import *

selection_fields = ["in_layer","expr","class","group"]

# TODO : manage duplicates
class SelectionItem(DictItem):

    def __init__(self,in_layer,expr,cls,group,code=None):
        dict = {"in_layer" : in_layer,
                "expr" : expr,
                "class" : cls,
                "group" : group}
        self.is_vector = isVectorPath(in_layer)
        self.is_raster = isRasterPath(in_layer)
        class_item = classes.classModel.getClassByName(cls)
        if not class_item:
            class_item = classes.ClassItem(cls,"",code)
            classes.classModel.addItem(class_item)
            classes.classModel.layoutChanged.emit()
        group_item = groups.groupsModel.getGroupByName(group)
        if not group_item:
            group_item = groups.GroupItem(group,"")
            groups.groupsModel.addItem(group_item)
            groups.groupsModel.layoutChanged.emit()
        #self.cls = cls
        super().__init__(dict)
        
    def checkParams(self):
        pass
        
    def applyItem(self):
        if self.is_vector:
            self.applyVectorItem()
            #self.applyRasterItem()
        elif self.is_raster:
            self.applyRasterItem()
        else:
            user_error("Unkown format for file '" + str(self.dict["in_layer"]))
        
    def applyVectorItem(self):
        debug("classModel = " + str(classes.classModel))
        in_layer_path = self.dict["in_layer"]
        checkFileExists(in_layer_path)
        in_layer = loadVectorLayer(in_layer_path)
        expr = self.dict["expr"]
        class_name = self.dict["class"]
        class_item = classes.getClassByName(class_name)
        group_name = self.dict["group"]
        group_item = groups.getGroupByName(group_name)
        out_vector_layer = group_item.vectorLayer
        if not out_vector_layer:
            out_vector_layer = createLayerFromExisting(in_layer,class_name + "_vector")
            orig_field = QgsField("Origin", QVariant.String)
            class_field = QgsField("Class", QVariant.String)
            code_field = QgsField("Code", QVariant.String)
            out_vector_layer.dataProvider().addAttributes([orig_field,class_field,code_field])
            out_vector_layer.updateFields()
        pr = out_vector_layer.dataProvider()
        if expr:
            feats = in_layer.getFeatures(QgsFeatureRequest().setFilterExpression(expr))
        else:
            feats = in_layer.getFeatures(QgsFeatureRequest())
        fields = out_vector_layer.fields()
        new_f = QgsFeature(fields)
        tmp_cpt = 0
        for f in feats:
            tmp_cpt += 1
            new_f.setGeometry(f.geometry())
            new_f["Origin"] = in_layer.name()
            new_f["Class"] = class_name
            new_f["Code"] = class_item.dict["code"]
            res = pr.addFeature(new_f)
            if not res:
                internal_error("ko")
            out_vector_layer.updateExtents()
        debug("length(feats) = " + str(tmp_cpt))
        group_item.vectorLayer = out_vector_layer
        if tmp_cpt == 0:
            warn("No entity selected from '" + str(self) + "'")
        group_item.saveVectorLayer()
        
        
    # def applyRasterItem(self):
        # debug("[applyItemRaster]")
        # field = "Code"
        # group_name = self.dict["group"]
        # group_item = groups.groupsModel.getGroupByName(group_name)
        # in_path = group_item.getVectorPath()
        # out_path = group_item.getRasterPath()
        # applyRasterization(in_path,field,out_path)
        
class SelectionModel(DictModel):
    
    def __init__(self):
        super().__init__(self,selection_fields)
        
    @staticmethod
    def mkItemFromDict(dict):
        checkFields(selection_fields,dict.keys())
        item = SelectionItem(dict["in_layer"],dict["expr"],dict["class"],dict["group"])
        return item

    def applyItems(self):
        selectionsByGroup = {}
        for i in self.items:
            grp = i.dict["group"]
            if grp in selectionsByGroup:
                selectionsByGroup[grp].append(i)
            else:
                selectionsByGroup[grp] = [i]
        for g, selections in selectionsByGroup.items():
            grp_item = groups.getGroupByName(g)
            for s in selections:
                s.applyVectorItem()
            grp_item.applyRasterizationItem()
        
class SelectionConnector(AbstractConnector):

    def __init__(self,dlg):
        self.dlg = dlg
        selectionModel = SelectionModel()
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
        self.dlg.selectionClassCombo.setModel(classes.classModel)
        self.dlg.selectionClassCombo.currentTextChanged.connect(self.setClass)
        self.dlg.selectionGroupCombo.setModel(groups.groupsModel)
        self.dlg.selectionGroupCombo.currentTextChanged.connect(self.setGroup)
        self.dlg.selectionRun.clicked.connect(self.model.applyItems)
        
    def setClass(self,text):
        self.dlg.selectionClass.setText(text)
        
    def setGroup(self,text):
        self.dlg.selectionGroup.setText(text)
                        
    def setInLayerFromCombo(self,layer):
        debug("setInLayerFromCombo")
        if layer:
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
        if layer:
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
        cls = self.dlg.selectionClass.text()
        group = self.dlg.selectionGroup.text()
        selection = SelectionItem(in_layer,expr,cls,group)
        return selection
        
    def mkItemsFromField(self):
        in_layer_path = self.dlg.selectionFieldLayer.filePath()
        in_layer = loadVectorLayer(in_layer_path)
        field_name = self.dlg.selectionField.currentField()
        group = self.dlg.selectionFieldGroup.text()
        field_values = set()
        for f in in_layer.getFeatures():
            field_values.add(f[field_name])
        debug(str(field_values))
        items = []
        for fv in field_values:
            grp_name = group + "_" + str(fv)
            class_item = classes.ClassItem(grp_name,"",int(fv))
            classes.classModel.addItem(class_item)
            classes.classModel.layoutChanged.emit()
            expr = "\"" + field_name + "\" = " + str(fv)
            item = SelectionItem(in_layer_path,expr,grp_name,group)
            items.append(item)
        return items
        
    def addItemsFromField(self):
        debug("[addItemsFromField]")
        items = self.mkItemsFromField()
        for i in items:
            self.model.addItem(i)
        self.model.layoutChanged.emit()
    