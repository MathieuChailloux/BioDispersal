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

from PyQt5.QtGui import QIcon
from qgis.core import QgsMapLayerProxyModel, Qgis
from qgis.gui import QgsFileWidget

from ..qgis_lib_mc import (utils, qgsUtils, abstract_model, qgsTreatments, feedbacks, styles)
from . import params, subnetworks

import time
import os

cost_fields = ["st_name","start_layer","perm_layer","cost","out_layer"]

# CostItem implements DictItem and contains below fields :
#   - 'st_name' : sous-trame name
#   - 'start_layer' : vector layer containing starting points
#   - 'perm_layer' : raster layer containing cost for each pixel
#   - 'cost' : maximal cost
class CostItem(abstract_model.DictItem):

    def __init__(self,st_name,start_layer,perm_layer,cost,out_layer):
        dict = {"st_name" : st_name,
                "start_layer" : start_layer,
                "perm_layer" : perm_layer,
                "cost" : cost,
                "out_layer" : out_layer}
        super().__init__(dict)
        
    def equals(self,other):
        same_start = self.dict["start_layer"] == other.dict["start_layer"]
        same_perm = self.dict["perm_layer"] == other.dict["perm_layer"]
        same_cost = self.dict["cost"] == other.dict["cost"]
        return (same_start and same_perm and same_cost)
            
    def checkItem(self):
        pass
        
class CostModel(abstract_model.DictModel):
    
    def __init__(self,bdModel):
        self.parser_name = "CostModel"
        self.is_runnable = True
        self.bdModel = bdModel
        super().__init__(self,cost_fields)
    
    def mkItemFromDict(self,dict):
        if "out_layer" in dict:
            utils.checkFields(cost_fields,dict.keys())
            item = CostItem(dict["st_name"],dict["start_layer"],dict["perm_layer"],
                            dict["cost"],dict["out_layer"])
        else:
            st_name = dict["st_name"]
            st_item = self.bdModel.stModel.getSTByName(st_name)
            out_path = st_item.getDispersionPath(dict["cost"])
            item = CostItem(dict["st_name"],dict["start_layer"],dict["perm_layer"],
                            dict["cost"],out_path)
        return item
        
    def applyItemWithContext(self,item,context,feedback):
        feedback.pushDebugInfo("Start runCost")
        # Parameters
        st_name = item.dict["st_name"]
        start_layer_path = self.bdModel.getOrigPath(item.dict["start_layer"])
        start_layer, start_layer_type = qgsUtils.loadLayerGetType(start_layer_path)
        cost = item.dict["cost"]
        perm_raster_path = self.bdModel.getOrigPath(item.dict["perm_layer"])
        tmp_path = self.bdModel.stModel.getDispersionTmpPath(st_name,cost)
        out_path = self.bdModel.getOrigPath(item.dict["out_layer"])
        if os.path.isfile(out_path):
            qgsUtils.removeRaster(out_path)
        # Feedback
        feedback.setProgressText("subnetwork " + st_name + ", max_cost : " + str(cost))
        step_feedback = feedbacks.ProgressMultiStepFeedback(10,feedback)
        step_feedback.setCurrentStep(0)
        # Processing
        if start_layer_type == 'Raster':
            start_raster_path = start_layer_path
            # TODO : WARP
        else:
            start_raster_path = self.bdModel.stModel.getStartLayerPath(st_name)
            crs, extent, resolution = self.bdModel.getRasterParams()
            qgsTreatments.applyRasterization(start_layer_path,start_raster_path,extent,resolution,
                                             burn_val=1,out_type=Qgis.Byte,nodata_val=0,all_touch=True,
                                             context=context,feedback=step_feedback)
        step_feedback.setCurrentStep(1)
        qgsTreatments.applyRCost(start_raster_path,perm_raster_path,cost,tmp_path,context=context,feedback=step_feedback)
        step_feedback.setCurrentStep(9)
        qgsTreatments.applyRasterCalcLE(tmp_path,out_path,cost,context=context,feedback=step_feedback)
        step_feedback.setCurrentStep(10)
        loaded_layer = qgsUtils.loadRasterLayer(out_path,loadProject=True)
        styles.setRandomColorRasterRenderer(loaded_layer)
        feedback.pushDebugInfo("End runCost")
        
    def applyItemsWithContext(self,indexes,context,feedback):
        feedbacks.beginSection("Computing dispersal")
        self.bdModel.paramsModel.checkInit()
        if not indexes:
            utils.internal_error("No indexes in Cost applyItems")
        nb_items = len(indexes)
        step_feedback = feedbacks.ProgressMultiStepFeedback(nb_items,feedback)
        curr_step = 0
        for n in indexes:
            i = self.items[n]
            self.applyItemWithContext(i,context,step_feedback)    
            curr_step += 1
            step_feedback.setCurrentStep(curr_step)        
            #i.applyItem(self.bdModel.stModel)
            #progress_section.next_step()
        feedbacks.endSection()
        
class CostConnector(abstract_model.AbstractConnector):

    def __init__(self,dlg,costModel):
        self.dlg = dlg
        self.onlySelection = False
        super().__init__(costModel,self.dlg.costView,
                         self.dlg.costAdd,self.dlg.costRemove,
                         self.dlg.costRun,self.dlg.costRunOnlySelection)
        
    def initGui(self):
        self.dlg.costStartLayerCombo.setFilters(QgsMapLayerProxyModel.VectorLayer)
        self.dlg.costStartLayer.setFilter(qgsUtils.getVectorFilters())
        self.dlg.costPermRasterCombo.setFilters(QgsMapLayerProxyModel.RasterLayer)
        self.dlg.costPermRaster.setFilter("*.tif")
        self.dlg.costOutLayer.setFilter("*.tif")
        self.dlg.costOutLayer.setStorageMode(QgsFileWidget.SaveFile)
        
    def connectComponents(self):
        super().connectComponents()
        self.dlg.costSTCombo.setModel(self.model.bdModel.stModel)
        self.dlg.costStartLayer.fileChanged.connect(self.setStartLayer)
        self.dlg.costPermRaster.fileChanged.connect(self.setPermRaster)
        
    def switchST(self,text):
        st_item = self.model.bdModel.stModel.getSTByName(text)
        st_friction_path = st_item.getFrictionPath()
        self.dlg.costPermRaster.lineEdit().setValue(st_friction_path)
        
    def setStartLayer(self,path):
        layer = qgsUtils.loadVectorLayer(path,loadProject=True)
        self.dlg.costStartLayerCombo.setLayer(layer)
        
    def setPermRaster(self,path):
        layer = qgsUtils.loadRasterLayer(path,loadProject=True)
        self.dlg.costPermRasterCombo.setLayer(layer)
        
    def setStartLayerFromCombo(self,layer):
        utils.debug("setStartLayerFromCombo")
        if layer:
            path = qgsUtils.pathOfLayer(layer)
            self.dlg.costStartLayer.lineEdit().setValue(path)
        
    def setPermRasterFromCombo(self,layer):
        utils.debug("setPermRasterFromCombo")
        if layer:
            path = qgsUtils.pathOfLayer(layer)
            self.dlg.costPermRaster.lineEdit().setValue(path)
        
    def mkItem(self):
        st_name = self.dlg.costSTCombo.currentText()
        if not st_name:
            utils.user_error("No Sous-Trame selected")
        start_layer = self.dlg.costStartLayerCombo.currentLayer()
        if not start_layer:
            utils.user_error("No start layer selected")
        start_layer_path = self.model.bdModel.normalizePath(qgsUtils.pathOfLayer(start_layer))
        perm_layer = self.dlg.costPermRasterCombo.currentLayer()
        if not perm_layer:
            utils.user_error("No permability layer selected")
        perm_layer_path = self.model.bdModel.normalizePath(qgsUtils.pathOfLayer(perm_layer))
        cost = str(self.dlg.costMaxVal.value())
        out_layer_path = self.model.bdModel.normalizePath(self.dlg.costOutLayer.filePath())
        cost_item = CostItem(st_name,start_layer_path,perm_layer_path,cost,out_layer_path)
        return cost_item
        