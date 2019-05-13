# -*- coding: utf-8 -*-
"""
/***************************************************************************
 BioDispersal
                                 A QGIS plugin
 Computes ecological continuities based on environments permeability
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2018-04-12
        git sha              : $Format:%H$
        copyright            : (C) 2018 by IRSTEA
        email                : mathieu.chailloux@irstea.fr
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import re

from PyQt5.QtCore import QCoreApplication
from qgis.core import QgsMapLayerProxyModel
from qgis.gui import QgsFileWidget

from ..qgis_lib_mc import utils, qgsUtils, qgsTreatments, abstract_model, feedbacks, styles
from . import params



ponderation_fields = ["mode","friction","ponderation","intervals","out_layer"]

pond_ival_fields = ["low_bound","up_bound","pond_value"]

float_re="\d+(?:\.\d+)?"
ival_re = "\(\[(" + float_re + "),(" + float_re + ")\],(" + float_re + ")\)"

class PondIvalItem(abstract_model.DictItem):

    LB = 'low_bound'
    UB = 'up_bound'
    PV = 'pond_value'

    def __init__(self,lb=0.0,ub=0.0,pv=1.0):
        dict = {"low_bound": lb,
                "up_bound" : ub,
                "pond_value" : pv}
        super().__init__(dict)
        
    def __str__(self):
        s = "([" + str(self.dict["low_bound"]) + ","
        s += str(self.dict["up_bound"]) + "],"
        s += str(self.dict["pond_value"]) + ")"
        return s
        
    def toIvalStr(self):
        s = str(self.dict["low_bound"])+ " - " + str(self.dict["up_bound"])
        return s
        
    @classmethod
    def fromStr(cls,s):
        match = re.search(ival_re,s)
        if match:
            lb = float(match.group(1))
            ub = float(match.group(2))
            pv = float(match.group(3))
            return cls(lb,ub,pv)
        else:
            utils.internal_error("No match for ponderation interval item in string '" + s + "'")
            
    def checkItem(self):
        if (self.dict["low_bound"] > self.dict["up_bound"]):
            utils.user_error("Ill-formed interval : " + str(self))
            
    def checkOverlap(self,other):
        if (self.dict["up_bound"] <= other.dict["low_bound"]):
            return -1
        elif (self.dict["low_bound"] >= other.dict["up_bound"]):
            return 1
        else:
            utils.user_error("Overlapping intervals : " + str(self) + " vs " + str(other))
        
class PondValueIvalItem(PondIvalItem):

    def __init__(self,lb=0.0,ub=0.0,pv=1.0):
        super().__init__(lb,ub,pv)

    def toGdalCalcExpr(self,idx):
        s = "(" + str(self.dict["pond_value"])
        s += "*A*less_equal(" + str(self.dict["low_bound"]) + ",B)"
        s += "*less(B," + str(self.dict["up_bound"]) + "))"
        return s
        
class PondBufferIvalItem(PondIvalItem):

    def __init__(self,lb=0.0,ub=0.0,pv=1.0):
        super().__init__(lb,ub,pv)

    def toGdalCalcExpr(self,idx):
        s = "(A==" + str(idx+2) + ")*" + str(self.dict["pond_value"])
        return s
        
        
class PondIvalModel(abstract_model.DictModel):
    
    def __init__(self):
        super().__init__(self,pond_ival_fields)
        
    def __str__(self):
        s = ""
        for i in self.items:
            if s != "":
                s += " - "
            s += str(i)
        return s
        
    def checkItems(self,i1,i2):
        if (i1.dict["up_bound"] <= i2.dict["low_bound"]):
            return -1
        elif (i1.dict["low_bound"] >= i2.dict["up_bound"]):
            return 1
        else:
            utils.user_error("Overlapping intervals : " + str(i1) + " vs " + str(i2))
        
    def checkModel(self):
        utils.debug("Checking model")
        n = len(self.items)
        for i1 in range(0,n):
            for i2 in range(i1+1,n):
                item1 = self.getNItem(i1)
                item2 = self.getNItem(i2)
                self.checkItems(item1,item2)
        
    def toGdalCalcExpr(self):
        s = ""
        for i in range(0,len(self.items)):
            ival = self.getNItem(i)
            if s != "":
                s+= " + "
            s += ival.toGdalCalcExpr(i)
        return s
        
    def toProcessingMatrix(self):
        m = []
        for i in self.items:
            m.append(i.dict["low_bound"])
            m.append(i.dict["up_bound"])
            m.append(i.dict["pond_value"])
        return m
        
class PondValueIvalModel(PondIvalModel):

    def __init__(self):
        super().__init__()
        
    @classmethod
    def fromStr(cls,s):
        res = cls()
        utils.debug("PondValueIvalModel.fromStr(" + str(s) +")")
        ivals = s.split('-')
        utils.debug("ivals = " + str(ivals))
        for ival_str in ivals:
            ival = PondValueIvalItem.fromStr(ival_str.strip())
            res.addItem(ival)
        return res
        
class PondBufferIvalModel(PondIvalModel):

    def __init__(self):
        super().__init__()
        self.max_val = None
        
    # def checkNotEmpty(self):
        # if len(self.items) == 0:
            # utils.internal_error("Empty buffer model")
        
    @classmethod
    def fromStr(cls,s):
        res = cls()
        utils.debug("PondBufferIvalModel.fromStr(" + str(s) +")")
        ivals = s.split('-')
        for ival_str in ivals:
            ival = PondBufferIvalItem.fromStr(ival_str)
            res.addItem(ival)
        return res
        
    def toDistances(self):
        nb_items = len(self.items)
        self.checkNotEmpty()
        distances = [i.dict["up_bound"] for i in self.items]
        return distances
        
    def toGdalCalcExpr(self):
        expr = super().toGdalCalcExpr()
        if not self.max_val:
            utils.internal_error("No max value for buffer model")
        expr += " + (A==1)"
        return expr
        
    def addItem(self,item):
        ub = item.dict["up_bound"]
        if not self.max_val or ub > self.max_val:
            self.max_val = ub
        super().addItem(item)
        
    def checkModel(self):
        self.checkNotEmpty()
        nb_items = len(self.items)
        if nb_items > 1:
            for i in range(0,nb_items-1):
                item = self.items[i]
                succ = self.items[i+1]
                item_ub = item.dict["up_bound"]
                succ_lb = succ.dict["low_bound"]
                if item_ub != succ_lb:
                    utils.user_error("Buffer model values are not continuous : '"
                                     + str(item_ub) + "' is not equal to '" + str(succ_lb) + "'")
                                     
    def toReclassDict(self):
        nb_itmes = len(self.items)
        res = {}
        for i in range(0,nb_items):
            res[i+2] = self.items[i]["pond_value"]
        return res
        
class PondValueIvalConnector(abstract_model.AbstractConnector):
    
    def __init__(self,dlg):
        self.dlg = dlg
        pondIvalModel = PondValueIvalModel()
        super().__init__(pondIvalModel,self.dlg.pondIvalView,
                         self.dlg.pondIvalPlus,self.dlg.pondIvalMinus)
                         
    def initGUi(self):
        pass
        
    def connectComponents(self):
        super().connectComponents()
        
    def mkItem(self):
        item = PondValueIvalItem()
        return item
        
class PondBufferIvalConnector(abstract_model.AbstractConnector):
    
    def __init__(self,dlg):
        self.dlg = dlg
        pondBufferModel = PondBufferIvalModel()
        self.onlySelection = False
        super().__init__(pondBufferModel,self.dlg.pondBufferView,
                         self.dlg.pondBufferPlus,self.dlg.pondBufferMinus)
                         
    def initGUi(self):
        pass
        
    def connectComponents(self):
        super().connectComponents()
        
    def mkItem(self):
        item = PondBufferIvalItem()
        return item
        

class PonderationItem(abstract_model.DictItem):
    
    def __init__(self,dict):
        super().__init__(dict)
        
    def applyMax(self,layer1,layer2,out_layer):
        qgsTreatments.applyMaxGdal(layer1,layer2,out_layer,load_flag=True)
        
    def applyMin(self,layer1,layer2,out_layer):
        weighting_params = { 'INPUT_LAYER' : layer1,
                             'WEIGHT_LAYER' : layer2,
                             'OPERATOR' : 0,
                             'OUTPUT' : out_layer }
        qgsTreatments.applyProcessingAlg('BioDispersal','weightingbasics',weighting_params)
        
        
class PonderationModel(abstract_model.DictModel):

    MIN_MODE = 0
    MAX_MODE = 1
    MULT_MODE = 2
    INTERVALS_MODE = 3
    BUFFER_MODE = 4

    def __init__(self,bdModel):
        self.parser_name = "PonderationModel"
        self.bdModel = bdModel
        super().__init__(self,ponderation_fields)
        
    def mkItemFromDict(self,dict):
        utils.checkFields(ponderation_fields,dict.keys())
        item = PonderationItem(dict)
        return item
        
    def applyItemWithContext(self,item,context,feedback):
        mode = int(item.dict["mode"])
        friction_layer_path = self.bdModel.getOrigPath(item.dict["friction"])
        pond_layer_path = self.bdModel.getOrigPath(item.dict["ponderation"])
        out_layer_path = self.bdModel.getOrigPath(item.dict["out_layer"])
        feedback.setProgressText("weighted layer " + item.dict["out_layer"])
        weighting_params = { 'INPUT_LAYER' : friction_layer_path,
                             'WEIGHT_LAYER' : pond_layer_path,
                             'RESAMPLING' : None,
                             'OUTPUT' : out_layer_path }
        if mode == self.MULT_MODE:
            weighting_params['OPERATOR'] = 2
            qgsTreatments.applyProcessingAlg('BioDispersal','weightingbasics',weighting_params,
                                             context=context,feedback=feedback)
        elif mode == self.INTERVALS_MODE:
            ival_model = PondValueIvalModel.fromStr(item.dict["intervals"])
            matrix = ival_model.toProcessingMatrix()
            weighting_params['INTERVALS'] = matrix
            qgsTreatments.applyProcessingAlg('BioDispersal','weightingbyintervals',weighting_params,
                                             context=context,feedback=feedback)
        elif mode == self.BUFFER_MODE:
            ival_model = PondBufferIvalModel.fromStr(item.dict["intervals"])
            matrix = ival_model.toProcessingMatrix()
            weighting_params['INTERVALS'] = matrix
            qgsTreatments.applyProcessingAlg('BioDispersal','weightingbydistance',weighting_params,
                                             context=context,feedback=feedback)
        elif mode == self.MAX_MODE:
            weighting_params['OPERATOR'] = 1
            qgsTreatments.applyProcessingAlg('BioDispersal','weightingbasics',weighting_params,
                                             context=context,feedback=feedback)
        elif mode == self.MIN_MODE:
            weighting_params['OPERATOR'] = 0
            qgsTreatments.applyProcessingAlg('BioDispersal','weightingbasics',weighting_params,
                                             context=context,feedback=feedback)
        else:
            utils.internal_error("Unexpected ponderation mode '" + str(mode) + "'")
        loaded_layer = qgsUtils.loadRasterLayer(out_layer_path,loadProject=True)
        styles.setRendererPalettedGnYlRd(loaded_layer)
                  
                    
class PonderationConnector(abstract_model.AbstractConnector):

    def __init__(self,dlg,ponderationModel):
        self.dlg = dlg
        super().__init__(ponderationModel,self.dlg.ponderationView,
                        self.dlg.pondAdd,self.dlg.pondRemove,
                        self.dlg.pondRun,self.dlg.pondRunOnlySelection)
                        
    def tr(self, message):
        return QCoreApplication.translate('BioDispersal', message)
        
    def initGui(self):
        self.dlg.pondFrictLayerCombo.setFilters(QgsMapLayerProxyModel.RasterLayer)
        self.dlg.pondOutLayer.setStorageMode(QgsFileWidget.SaveFile)
        self.dlg.pondOutLayer.setFilter("*.tif")
        self.dlg.pondLayerCombo.setFilters(QgsMapLayerProxyModel.RasterLayer)
        self.dlg.pondLayer.setStorageMode(QgsFileWidget.GetFile)
        self.dlg.pondModeCombo.addItem(self.tr("Minimum"))
        self.dlg.pondModeCombo.addItem(self.tr("Maximum"))
        self.dlg.pondModeCombo.addItem(self.tr("Multiplication"))
        self.dlg.pondModeCombo.addItem(self.tr("Intervalles"))
        self.dlg.pondModeCombo.addItem(self.tr("Tampons"))
        self.dlg.pondModeCombo.setCurrentIndex(0)
        self.activateDirectMode()
        
    def connectComponents(self):
        super().connectComponents()
        self.dlg.pondFrictLayer.fileChanged.connect(self.setFrictionLayer)
        self.dlg.pondLayer.fileChanged.connect(self.setPondLayer)
        self.valueConnector = PondValueIvalConnector(self.dlg)
        self.valueConnector.connectComponents()
        self.bufferConnector = PondBufferIvalConnector(self.dlg)
        self.bufferConnector.connectComponents()
        self.dlg.pondModeCombo.currentIndexChanged.connect(self.switchPondMode)
    
    def mkItem(self):
        mode = self.dlg.pondModeCombo.currentIndex()
        friction_layer = self.dlg.pondFrictLayerCombo.currentLayer()
        friction_layer_path = self.model.bdModel.normalizePath(qgsUtils.pathOfLayer(friction_layer))
        pond_layer = self.dlg.pondLayerCombo.currentLayer()
        pond_layer_path = self.model.bdModel.normalizePath(qgsUtils.pathOfLayer(pond_layer))
        out_path = self.model.bdModel.normalizePath(self.dlg.pondOutLayer.filePath())
        if not out_path:
            utils.user_error("No output path selected for ponderation")
        if mode in [PonderationModel.MIN_MODE,PonderationModel.MAX_MODE,PonderationModel.MULT_MODE]:
            ivals =  ""
        elif mode == PonderationModel.INTERVALS_MODE:
            ivals = str(self.valueConnector.model)
        elif mode == PonderationModel.BUFFER_MODE:
            ivals = str(self.bufferConnector.model)
        else:
            utils.internal_error("Unexpected ponderation mode '" + str(mode) + "'")
        dict = { "mode" : mode,
                 "intervals" : ivals,
                 "friction" : friction_layer_path,
                 "ponderation" : pond_layer_path,
                 "out_layer" : out_path
                }
        item = PonderationItem(dict)
        return item
        
    def applyItems(self):
        feedbacks.beginSection("Weighting")
        super().applyItems()
        feedbacks.endSection()
        
    def setFrictionLayer(self,path):
        loaded_layer = qgsUtils.loadRasterLayer(path,loadProject=True)
        self.dlg.pondFrictLayerCombo.setLayer(loaded_layer)
        
    def setPondLayer(self,path):
        loaded_layer = qgsUtils.loadRasterLayer(path,loadProject=True)
        self.dlg.pondLayerCombo.setLayer(loaded_layer)
    
    def switchPondMode(self,mode):
        if mode in [PonderationModel.MIN_MODE,PonderationModel.MAX_MODE,PonderationModel.MULT_MODE]:
            self.activateDirectMode()
        elif mode == PonderationModel.INTERVALS_MODE:
            self.activateIvalMode()
        elif mode == PonderationModel.BUFFER_MODE:
            self.activateBufferMode()
        else:
            utils.internal_error("Unexpected ponderation mode '" + str(mode) + "'")
        
    
    def activateDirectMode(self):
        utils.debug("activateDirectMode")
        self.dlg.stackPond.hide()
        
    def activateIvalMode(self):
        utils.debug("activateIvalMode")
        self.dlg.stackPond.show()
        self.dlg.stackPond.setCurrentWidget(self.dlg.stackPondIval)
        
    def activateBufferMode(self):
        utils.debug("activateBufferMode")
        self.dlg.stackPond.show()
        self.dlg.stackPond.setCurrentWidget(self.dlg.stackPondBuffer)
    
    
    
    