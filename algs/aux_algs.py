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

import os
import math
import xml.etree.ElementTree as ET
    
from PyQt5.QtCore import QCoreApplication, QVariant
from PyQt5.QtGui import QIcon
from qgis.core import (Qgis,
                       QgsField,
                       QgsProcessing,
                       QgsProcessingUtils,
                       QgsProcessingAlgorithm,
                       QgsProcessingException,
                       QgsProcessingMultiStepFeedback,
                       QgsProcessingParameterDefinition,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterExtent,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterMatrix,
                       QgsProcessingParameterExpression,
                       QgsProcessingParameterString,
                       QgsProcessingParameterField,
                       QgsProcessingParameterRange,
                       QgsProcessingParameterVectorDestination,
                       QgsProcessingParameterRasterDestination,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingParameterFolderDestination,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterMapLayer,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterFile,
                       QgsFeatureSink)

import processing
from processing.algs.gdal.rasterize import rasterize

from ..qgis_lib_mc import utils, qgsUtils, qgsTreatments, feedbacks, styles

AuxAlgorithm = qgsUtils.BaseProcessingAlgorithm
               
class BioDispersalAlgorithm(AuxAlgorithm):

    ALG_NAME = 'BioDispersalAlgorithm'
    
    # Algorithm parameters
    INPUT_CONFIG = "INPUT"
    LOG_FILE = "LOG"
        
    def displayName(self):
        return self.tr("Run BioDispersal from configuration file")
    def group(self):
        return self.tr("Misc")
    def groupId(self):
        return 'misc'
        
    def shortHelpString(self):
        return self.tr("Executes complete process from XML configuration file")

    def initAlgorithm(self,config=None):
        self.addParameter(
            QgsProcessingParameterFile(
                self.INPUT_CONFIG,
                description=self.tr("Input configuration file")))
        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.LOG_FILE,
                description=self.tr("Log file")))
                
    def processAlgorithm(self,parameters,context,feedback):
        feedback.pushInfo("begin")
        utils.print_func = feedback.pushInfo
        # Parameters
        log_file = self.parameterAsFile(parameters,self.LOG_FILE,context)
        feedback.pushDebugInfo("log file = " + str(log_file))
        if utils.fileExists(log_file):
            os.remove(log_file)
        with open(log_file,"w+") as f:
            f.write("BioDispersal from configuration file " + str(log_file) + "\n")
            #raise QgsProcessingException("Log file " + str(log_file) + " already exists")
        log_feedback = feedbacks.FileFeedback(log_file)
        log_feedback.pushInfo("File feedback initialized")
        config_file = self.parameterAsFile(parameters,self.INPUT_CONFIG,context)
        config_tree = ET.parse(config_file)
        config_root = config_tree.getroot()
        bdModel = BioDispersalModel(context,log_feedback)
        log_feedback.pushInfo("from log")
        bdModel.feedback.pushInfo("from model")
        bdModel.fromXMLRoot(config_root)
        bdModel.runModel()
        outputs = [bdModel.getOrigPath(item.dict["out_layer"]) for item in bdModel.costModel.items]
        #qgsUtils.loadVectorLayer(res,loadProject=True)
        return {self.OUTPUT: outputs}
               
   
class RasterSelectionByValue(AuxAlgorithm):

    ALG_NAME = 'rasterselectionbyvalue'

    OPERATOR = 'OPERATOR'
    VALUE = 'VALUE'
    
    OPERATORS = ['<','<=','>','>=','==','!=']
    OPERATORS_CMPL = ['>=','>','<=','<','!=','==']
        
    def displayName(self):
        return self.tr('Raster selection by value')
    def group(self):
        return self.tr("Misc")
    def groupId(self):
        return 'misc'
        
    def shortHelpString(self):
        return self.tr('Creates new raster with input raster values veryfing specified operation.')

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT,
                description=self.tr('Input layer')))
        self.addParameter(
            QgsProcessingParameterEnum(self.OPERATOR,
                                       self.tr('Operator'),
                                       options=self.OPERATORS,
                                       defaultValue=4))
        self.addParameter(
            QgsProcessingParameterNumber (
                self.VALUE,
                description=self.tr('Value'),
                defaultValue=0.0,
                type=QgsProcessingParameterNumber.Double))
        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.OUTPUT,
                self.tr("Output layer")))
                
                
    def processAlgorithm(self,parameters,context,feedback):
        input = self.parameterAsRasterLayer(parameters,self.INPUT,context)
        if input is None:
            raise QgsProcessingException(self.invalidRasterError(parameters, self.INPUT))
        operator = self.parameterAsEnum(parameters,self.OPERATOR,context)
        value = self.parameterAsDouble(parameters,self.VALUE,context)
        output = self.parameterAsOutputLayer(parameters, self.OUTPUT, context)
        # Type
        input_type = input.dataProvider().sourceDataType(1)
        # Expression
        input_nodata_val = input.dataProvider().sourceNoDataValue(1)
        operator_str = self.OPERATORS[operator]
        operator_cmpl_str = self.OPERATORS_CMPL[operator]
        value_str = str(value)
        nodata_str = str(input_nodata_val)
        cmp_expr = '(A {} {})'.format(operator_str,value_str)
        cmp_expr_cmpl = '(A {} {})'.format(operator_cmpl_str,value_str)
        expr = "A * " + str(cmp_expr)
        mult_expr = "A * B"
        if math.isnan(input_nodata_val):
            nodata_val = None
        else:
            nodata_val = input_nodata_val
        feedback.pushDebugInfo("nodata_val = " + nodata_str)
        feedback.pushDebugInfo("gdalcalc expr = " + str(expr))
        # Call
        tmp = QgsProcessingUtils.generateTempFilename('tmp.tif')
        out = qgsTreatments.applyRasterCalc(input,tmp,expr,
                                      nodata_val=0,out_type=input_type,
                                      context=context,feedback=feedback)
        out = qgsTreatments.applyRSetNull(tmp,0,output,context,feedback)
        return { 'OUTPUT' : out }
                
    
class RasterizeFixAllTouch(AuxAlgorithm,rasterize):

    ALG_NAME = 'rasterizefixalltouch'
        
    def displayName(self):
        return self.tr('Rasterize (with ALL_TOUCH fix)')
    def group(self):
        return self.tr("Misc")
    def groupId(self):
        return 'misc'
        
    #def group(self):
    #    return "Auxiliary algorithms"
        
    #def groupId(self):
    #    return 'aux'
        
    def shortHelpString(self):
        return self.tr('Wrapper for gdal:rasterize algorithm allowing to use ALL_TOUCH option (every pixel touching input geometry are rasterized).')

    def initAlgorithm(self, config=None):
        super().initAlgorithm(config)
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.ALL_TOUCH,
                description = 'ALL_TOUCH option',
                defaultValue=False,
                optional=True))
    
# Apply rasterization on field 'field' of vector layer 'in_path'.
# Output raster layer in 'out_path'.
# Resolution set to 25 if not given.
# Extent can be given through 'extent_path'. If not, it is extracted from input layer.
# Output raster layer is loaded in QGIS if 'load_flag' is True.
def applyRasterizationFixAllTouch(in_path,out_path,extent,resolution,
                   field=None,burn_val=None,out_type=Qgis.Float32,
                   nodata_val=qgsTreatments.nodata_val,all_touch=False,overwrite=False,
                   context=None,feedback=None):
    #TYPES = ['Byte', 'Int16', 'UInt16', 'UInt32', 'Int32', 'Float32', 'Float64', 'CInt16', 'CInt32', 'CFloat32', 'CFloat64']
    out_type = qgsTreatments.qgsTypeToInt(out_type,shift=True)
    if overwrite:
        qgsUtils.removeRaster(out_path)
    extra_param_name = 'EXTRA'
    if hasattr(rasterize,extra_param_name):
        res = qgsTreatments.applyRasterization(in_path,out_path,extent,resolution,
                field=field,burn_val=burn_val,out_type=out_type,
                nodata_val=nodata_val,all_touch=all_touch,overwrite=overwrite,
                context=context,feedback=feedback)
    else:
        parameters = { 'ALL_TOUCH' : True,
                   'BURN' : burn_val,
                   'DATA_TYPE' : out_type,
                   'EXTENT' : extent,
                   'FIELD' : field,
                   'HEIGHT' : resolution,
                   'INPUT' : in_path,
                   'NODATA' : nodata_val,
                   'OUTPUT' : out_path,
                   'UNITS' : 1, 
                   'WIDTH' : resolution }
        res = qgsTreatments.applyProcessingAlg("BioDispersal",
            "rasterizefixalltouch",parameters,context,feedback)
    return res
    
    
class ChangeNoDataVal(AuxAlgorithm):

    ALG_NAME = 'changenodata'
    
    NODATA_VAL = 'NODATA_VAL'
        
    def displayName(self):
        return self.tr('Change NoData value')
    def group(self):
        return self.tr("Misc")
    def groupId(self):
        return 'misc'
        
    def shortHelpString(self):
        return self.tr('Change NoData value and reclassifies old NoData pixels to new NoData value.')

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT,
                description=self.tr('Input layer')))
        self.addParameter(
            QgsProcessingParameterNumber (
                self.NODATA_VAL,
                description=self.tr('New NoData value'),
                type=QgsProcessingParameterNumber.Double))
        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.OUTPUT,
                self.tr("Output layer")))
                
    def processAlgorithm(self,parameters,context,feedback):
        input = self.parameterAsRasterLayer(parameters,self.INPUT,context)
        if input is None:
            raise QgsProcessingException(self.invalidRasterError(parameters, self.INPUT))
        new_val = self.parameterAsDouble(parameters,self.NODATA_VAL,context)
        output = self.parameterAsOutputLayer(parameters, self.OUTPUT, context)
        input_nodata_val = input.dataProvider().sourceNoDataValue(1)
        feedback.pushDebugInfo("Input NoData value = " + str(input_nodata_val))
        #input_vals = qgsUtils.getRasterValsBis(input)
        input_vals = qgsTreatments.getRasterUniqueVals(input,feedback)
        feedback.pushDebugInfo("Input values = " + str(input_vals))
        if input_vals == []:
            feedback.pushInfo("Empty input layer (no input values)")
        if new_val in input_vals:
            raise QgsProcessingException("Input layer contains pixels with new NoData value '"
                    + str(new_val) + "'.")
        tmp = QgsProcessingUtils.generateTempFilename('tmp.tif')
        qgsTreatments.applyRNull(input,new_val,tmp,context,feedback)
        qgsTreatments.applyRSetNull(tmp,new_val,output,context,feedback)
        return { 'OUTPUT' : output }
