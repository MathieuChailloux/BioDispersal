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
from abc import ABC, abstractmethod

try:
    import numpy as np
except:
    pass
try:
    from osgeo import gdal
except ImportError:
    import gdal
    
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
                       QgsProcessingParameterFeatureSink,
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
                       QgsProcessingParameterFile)

import processing
from processing.algs.gdal.rasterize import rasterize

from ..qgis_lib_mc import utils, qgsUtils, qgsTreatments, feedbacks, styles

class PatchAlgorithm(qgsUtils.BaseProcessingAlgorithm):

    def group(self):
        return self.tr("Patch utils (raster)")
    def groupId(self):
        return 'patch'
        
    def debugRaster(self,feedback,arr,inputPath,outName,
            nodata=-9999,type=gdal.GDT_Float32):
        if self.DEBUG:
            feedback.pushDebugInfo(outName + " = " + str(arr))
            feedback.pushDebugInfo(outName + ".dtype = " + str(arr.dtype))
            outPath = QgsProcessingUtils.generateTempFilename(outName + ".tif")
            feedback.pushDebugInfo(outName + "path = " + str(outPath))
            qgsUtils.exportRaster(arr,inputPath,outPath,nodata=nodata,type=type)

class DistanceToBorderVector(PatchAlgorithm):

    ALG_NAME = 'distanceToBorderVector'
    
    EXTENT = 'EXTENT'
    RESOLUTION = 'RESOLUTION'
    
    def displayName(self):
        return self.tr("Distance to borders (vector)")
        
    def shortHelpString(self):
        return self.tr("Distance to border")
        
    def initAlgorithm(self, config=None, report_opt=True):
        self.addParameter(QgsProcessingParameterMapLayer(
            self.INPUT,
            "Input landuse layer",
            types=[Qgis.Polygon]))
        self.addParameter(QgsProcessingParameterExtent(
            self.EXTENT,
            "Output extent"))
        self.addParameter(QgsProcessingParameterNumber(
            self.RESOLUTION,
            "Output resolution",
            defaultValue=10.0,
            type=QgsProcessingParameterNumber.Double))
        self.addParameter(QgsProcessingParameterRasterDestination(
            self.OUTPUT,
            self.tr("Output layer")))
            
    def processAlgorithm(self,parameters,context,feedback):
        input = self.parameterAsMapLayer(parameters,self.INPUT,context)
        if input is None:
            raise QgsProcessingException(self.invalidRasterError(parameters, self.INPUT))
        extent = self.parameterAsExtent(parameters,self.EXTENT,context)
        resolution = self.parameterAsDouble(parameters,self.RESOLUTION,context)
        output = self.parameterAsOutputLayer(parameters, self.OUTPUT, context)
        # Processing
        border_path = self.mkTmpPath('borders.gpkg')
        # type = 2 <=> LineString
        qgsTreatments.convertGeomType(input,2,border_path,context,feedback)
        border_raster_path = self.mkTmpPath('borders.tif')
        qgsTreatments.applyRasterization(border_path,border_raster_path,
            extent,resolution,burn_val=1,out_type=Qgis.Byte,
            context=context,feedback=feedback)

   

class DistanceToBorderRaster(PatchAlgorithm):

    ALG_NAME = 'distanceToBorderRaster'
    
    def displayName(self):
        return self.tr("Distance to borders (Raster)")
        
    def shortHelpString(self):
        return self.tr("Distance for each pixel to patch border.")
        
    def initAlgorithm(self, config=None, report_opt=True):
        self.addParameter(QgsProcessingParameterRasterLayer(
            self.INPUT,
            "Input landuse layer"))
        self.addParameter(QgsProcessingParameterRasterDestination(
            self.OUTPUT,
            self.tr("Output layer")))
            
    def processAlgorithm(self,parameters,context,feedback):
        input = self.parameterAsRasterLayer(parameters,self.INPUT,context)
        if input is None:
            raise QgsProcessingException(self.invalidRasterError(parameters, self.INPUT))
        output = self.parameterAsOutputLayer(parameters, self.OUTPUT, context)
        # Processing
        extent = input.extent()
        input_nodata = input.dataProvider().sourceNoDataValue(1)
        unique_vals = qgsTreatments.getRasterUniqueVals(input,feedback)
        nb_vals = len(unique_vals)
        mf = QgsProcessingMultiStepFeedback(nb_vals * 2 + 2, feedback)
        prox_layers = []
        mf.pushDebugInfo("classes = " + str(unique_vals))
        for count, v in enumerate(unique_vals,start=0):
            classes = list(unique_vals)
            classes.remove(v)
            mf.pushDebugInfo("classes = " + str(classes))
            classes_str = ",".join([str(c) for c in classes])
            mf.pushDebugInfo("classes_str = " + str(classes_str))
            prox_v_path = self.mkTmpPath("proximity_" + str(v) + ".tif")
            qgsTreatments.applyProximity(input,prox_v_path,classes=classes_str,context=context,feedback=mf)
            mf.setCurrentStep(count * 2 + 1)
            prox_vnull_path = self.mkTmpPath("proximity_" + str(v) + "_null.tif")
            # expr_v = "logical_and(A != " + str(v) + ", A != " + str(input_nodata) + ") * B"
            # qgsTreatments.applyRasterCalcAB(input,prox_v_path,prox_vnull_path,expr_v,
                # nodata_val=0,context=context,feedback=mf)
            extract_params = { RasterSelectionByValue.INPUT : prox_v_path,
                RasterSelectionByValue.OPERATOR : 2,
                RasterSelectionByValue.VALUE : 0,
                RasterSelectionByValue.OUTPUT : prox_vnull_path
            }
            processing.run("BioDispersal:" + RasterSelectionByValue.ALG_NAME,
                extract_params,context=context,feedback=mf)
            prox_layers.append(prox_vnull_path)
            # qgsUtils.removeRaster(prox_v_path)
            mf.setCurrentStep(count * 2 + 2)
        min_prox_path = self.mkTmpPath("min_prox.tif")
        qgsTreatments.applyRSeries(prox_layers,4,min_prox_path,
            context=context,feedback=mf)
        mf.setCurrentStep(nb_vals+1)
        expr = "((A != " + str(input_nodata) + ") * B)"
        qgsTreatments.applyRasterCalcAB(input,min_prox_path,output,expr,
            nodata_val=0,context=context,feedback=mf)
        mf.setCurrentStep(nb_vals+2)
        return { self.OUTPUT : output }
        
        
try:
    import scipy
    from scipy import ndimage
    import_scipy_ok = True
except ImportError:
    import_scipy_ok = False
    

class LabelPatches(PatchAlgorithm):

    ALG_NAME = 'labelPatches'
    
    def displayName(self):
        return self.tr("Label patches")
        
    def shortHelpString(self):
        return self.tr("Patch labelling")
        
    def initAlgorithm(self, config=None, report_opt=True):
        self.addParameter(QgsProcessingParameterRasterLayer(
            self.INPUT,
            "Input layer"))
        self.addParameter(QgsProcessingParameterRasterDestination(
            self.OUTPUT,
            self.tr("Output layer")))
            
    def processAlgorithm(self,parameters,context,feedback):
        # Import scipy
        if not utils.scipyIsInstalled():
            msg = "Scipy (python library) import failed. You can install it through OSGEO installer"
            raise QgsProcessingException(msg)
        import scipy
        # Parse params
        input = self.parameterAsRasterLayer(parameters,self.INPUT,context)
        if input is None:
            raise QgsProcessingException(self.invalidRasterError(parameters, self.INPUT))
        input_path = qgsUtils.pathOfLayer(input)
        output = self.parameterAsOutputLayer(parameters, self.OUTPUT, context)
        # Processing
        classes, array = qgsUtils.getRasterValsAndArray(input_path)
        mf = QgsProcessingMultiStepFeedback(len(classes), feedback)
        struct = scipy.ndimage.generate_binary_structure(2,1)
        res_array = np.zeros(array.shape)
        class_array = np.copy(array)
        prev_nb_patches = 0
        for count, c in enumerate(classes,start=1):
            # mf.pushDebugInfo("Labelling class " + str(c))
            class_array[array==c] = 1
            class_array[array!=c] = 0
            labeled_array, nb_patches = scipy.ndimage.label(class_array,struct)
            mf.pushDebugInfo("labeled_array = " + str(labeled_array))
            labeled_array[array==c] += prev_nb_patches
            mf.pushDebugInfo("labeled_array = " + str(labeled_array))
            tmp_path = self.mkTmpPath("labeled_" + str(c) + ".tif")
            # qgsUtils.exportRaster(res_array,input_path,tmp_path)
            res_array = np.add(res_array,labeled_array)
            mf.pushDebugInfo("res_array = " + str(res_array))
            prev_nb_patches += nb_patches
            mf.setCurrentStep(count)
        qgsUtils.exportRaster(res_array,input_path,output,nodata=0,type=gdal.GDT_UInt32)
        return {self.OUTPUT : output}
    

class PatchSizeRaster(PatchAlgorithm):

    ALG_NAME = 'patchSizeRaster'
    LABELLED = 'LABELLED'
    
    def displayName(self):
        return self.tr("Patch size")
        
    def shortHelpString(self):
        return self.tr("Computes patch size (pixel value = pixel patch size)")
        
    def initAlgorithm(self, config=None, report_opt=True):
        self.addParameter(QgsProcessingParameterRasterLayer(
            self.INPUT,
            "Input layer"))
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.LABELLED,
                description = 'Input is already labelled',
                defaultValue=False,
                optional=True))
        self.addParameter(QgsProcessingParameterRasterDestination(
            self.OUTPUT,
            self.tr("Output layer")))
            
    def processAlgorithm(self,parameters,context,feedback):
        # Import scipy
        if not utils.scipyIsInstalled():
            msg = "Scipy (python library) import failed. You can install it through OSGEO installer"
            raise QgsProcessingException(msg)
        import scipy
        # Parse params
        input = self.parameterAsRasterLayer(parameters,self.INPUT,context)
        if input is None:
            raise QgsProcessingException(self.invalidRasterError(parameters, self.INPUT))
        input_path = qgsUtils.pathOfLayer(input)
        is_labelled = self.parameterAsBool(parameters,self.LABELLED,context)
        output = self.parameterAsOutputLayer(parameters, self.OUTPUT, context)
        # Labelling
        if is_labelled:
            labelled_path = input_path
        else:
            labelled_path = self.mkTmpPath("labelled.tif")
            label_params = { LabelPatches.INPUT : input,
                LabelPatches.OUTPUT : labelled_path }
            processing.run("BioDispersal:" + LabelPatches.ALG_NAME,
                label_params,context=context,feedback=feedback)
        classes, array = qgsUtils.getRasterValsAndArray(labelled_path)
        # Labelling new
        #Computing size new
        values, counts = np.unique(array, return_counts=True)
        replacer = { v : c for v, c in zip(values,counts)}
        val_arr = np.array(values)
        count_arr = np.array(counts)
        mapping_arr = np.zeros(val_arr.max()+1,dtype=count_arr.dtype)
        mapping_arr[val_arr]= count_arr
        feedback.pushDebugInfo("mapping_arr = " + str(mapping_arr))
        res_array = mapping_arr[array]
        res_array[array == 0] = 0
        # Computing size
        # mf = QgsProcessingMultiStepFeedback(len(classes), feedback)
        # res_array = np.zeros(array.shape)
        # for count, c in enumerate(classes,start=1):
            # nb_pix = np.count_nonzero(array == c)
            # res_array[array==c] = nb_pix
            # mf.setCurrentStep(count)
        qgsUtils.exportRaster(res_array,input_path,output,nodata=0,type=gdal.GDT_UInt32)
        return {self.OUTPUT : output}
        

class NeighboursCount(PatchAlgorithm):

    ALG_NAME = 'neigboursCount'
    
    def displayName(self):
        return self.tr("Neigbours count")
        
    def shortHelpString(self):
        return self.tr("Computes for each pixel the number of immediate neighbours of same value")
    
    def initAlgorithm(self, config=None, report_opt=True):
        self.addParameter(QgsProcessingParameterRasterLayer(
            self.INPUT,
            "Input layer"))
        self.addParameter(QgsProcessingParameterRasterDestination(
            self.OUTPUT,
            self.tr("Output layer")))
            
    def processAlgorithm(self,parameters,context,feedback):
        input = self.parameterAsRasterLayer(parameters,self.INPUT,context)
        if input is None:
            raise QgsProcessingException(self.invalidRasterError(parameters, self.INPUT))
        output = self.parameterAsOutputLayer(parameters, self.OUTPUT, context)
        # Processing
        in_path = qgsUtils.pathOfLayer(input)
        in_nodata = input.dataProvider().sourceNoDataValue(1)
        classes, array = qgsUtils.getRasterValsAndArray(in_path)
        struct = ndimage.generate_binary_structure(2,1)
        nb_neighbours_arr = ndimage.generic_filter(array,
            self.countNeighbours,footprint=struct, mode="constant",cval=in_nodata)
        qgsUtils.exportRaster(nb_neighbours_arr,input.source(),output)
        return {self.OUTPUT : output}
            
    def countNeighbours(self,array):
        cell_val = array[2]
        return np.count_nonzero(array == cell_val) - 1
        
    
class ExtractPatchesR(PatchAlgorithm):

    ALG_NAME = 'extractPatchesR'
        
    VALUES = 'VALUES'
    SURFACE = 'SURFACE'
            
    def displayName(self):
        return self.tr('Extract patches (Raster to Raster)')
    
    def shortHelpString(self):
        s = "Extract patches from land use raster layer according to"
        s += " specified land use types and minimum surface."
        s += "\nLand use values are integer separated by semicolons (';')."
        return self.tr(s)

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT,
                description=self.tr('Input layer')))
        self.addParameter(
            QgsProcessingParameterString (
                self.VALUES,
                description=self.tr('Land use values (separated by \';\')')))
        self.addParameter(
            QgsProcessingParameterNumber (
                self.SURFACE,
                description=self.tr('Patch minimum surface (square meters)'),
                type=QgsProcessingParameterNumber.Double,
                optional=True))
        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.OUTPUT,
                self.tr("Output layer")))
                
    def processAlgorithm(self,parameters,context,feedback):
        # Check numpy dependency
        if not utils.numpyIsInstalled():
            msg = "Numpy (python library) import failed. You can install it through OSGEO installer"
            raise QgsProcessingException(msg)
        import numpy as np
        # Parse inputs
        input = self.parameterAsRasterLayer(parameters,self.INPUT,context)
        if input is None:
            raise QgsProcessingException(self.invalidRasterError(parameters, self.INPUT))
        values = self.parameterAsInts(parameters,self.VALUES,context)
        surface = self.parameterAsDouble(parameters,self.SURFACE,context)
        feedback.pushDebugInfo("values = " + str(values))
        nb_vals = len(values)
        if nb_vals == 0:
            raise QgsProcessingException("No land use values specified (check string format)")
        output = self.parameterAsOutputLayer(parameters, self.OUTPUT, context)
        # Expression
        input_nodata_val = input.dataProvider().sourceNoDataValue(1)
        if nb_vals == 1:
            expr_str = 'A == {}'.format(values[0])
        else:
            expr_str = ''
            for v in values[:-1]:
                expr_str += 'logical_or(A == {},'.format(v)
            expr_str += 'A == {}'.format(values[-1])
            expr_str += ")" * (nb_vals - 1)
        feedback.pushDebugInfo("raster calc expr = " + expr_str)
        # Raster calc
        selection_path = QgsProcessingUtils.generateTempFilename('landuse_selection.tif')
        out_calc = selection_path if surface else output
        qgsTreatments.applyRasterCalc(input,out_calc,expr_str,
                                      nodata_val=0,out_type=0,
                                      context=context,feedback=feedback)
        # Labelling : reprendre
        if surface:
            if not (utils.scipyIsInstalled() and utils.numpyIsInstalled()):
                raise QgsProcessingException("Import of numpy/scipy failed, please install these libraries from OSGEO installer")
            from scipy import ndimage
            size_path = qgsUtils.mkTmpPath("size.tif")
            # Compute patch size
            patch_params = { PatchSizeRaster.INPUT : selection_path,
                PatchSizeRaster.OUTPUT : size_path }
            processing.run("BioDispersal:" + PatchSizeRaster.ALG_NAME,
                patch_params,context=context,feedback=feedback)
            # Convert surface
            x_res = input.rasterUnitsPerPixelX()
            y_res = input.rasterUnitsPerPixelY()
            surface_pixel = surface / (x_res * y_res)
            feedback.pushDebugInfo("surface_pixel = " + str(surface_pixel))
            # Filter by size
            size_vals, size_arr = qgsUtils.getRasterValsAndArray(size_path)
            size_arr[size_arr<surface_pixel] = 0
            size_arr[size_arr>=surface_pixel] = 1
            # Export
            qgsUtils.exportRaster(size_arr,input.source(),output,nodata=0,type=gdal.GDT_Byte)
        # return
        return { 'OUTPUT' : output }
        