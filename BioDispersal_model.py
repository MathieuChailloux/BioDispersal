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

from .qgis_lib_mc import utils
from .steps import (params, subnetworks, groups, classes, selection,
                    fusion, friction, ponderation, cost)

class BioDispersalModel:

    def __init__(self,context,feedback):
        self.parser_name = "ModelConfig"
        self.context = None
        self.feedback = feedback
        self.feedback.pushDebugInfo("feedback bd = " + str(feedback))
        self.paramsModel = params.ParamsModel(self)
        self.stModel = subnetworks.STModel(self)
        self.selectionModel = selection.SelectionModel(self)
        self.classModel = classes.ClassModel(self)
        self.groupsModel = groups.GroupModel(self)
        self.fusionModel = fusion.FusionModel(self)
        self.frictionModel = friction.FrictionModel(self)
        self.ponderationModel = ponderation.PonderationModel(self)
        self.costModel = cost.CostModel(self)
        self.models = [self.paramsModel, self.stModel, self.groupsModel, self.classModel,
                       self.selectionModel, self.fusionModel, self.frictionModel,
                       self.ponderationModel, self.costModel]
        self.parser_name = "BioDispersalModel"
        
    def checkWorkspaceInit(self):
        self.paramsModel.checkWorkspaceInit()
            
    # Returns relative path w.r.t. workspace directory.
    # File separator is set to common slash '/'.
    def normalizePath(self,path):
        return self.paramsModel.normalizePath(path)
            
    # Returns absolute path from normalized path (cf 'normalizePath' function)
    def getOrigPath(self,path):
        return self.paramsModel.getOrigPath(path)
    
    def mkOutputFile(self,name):
        return self.paramsModel.mkOutputFile(name)
        
    def getRasterParams(self):
        crs = self.paramsModel.crs
        extent = self.paramsModel.getExtentString()
        resolution = self.paramsModel.getResolution()
        return (crs, extent, resolution)
        
    def runModel(self):
        self.feedback.pushDebugInfo("feedback fs rm = " + str(self.feedback))
        for model in self.models:
            self.feedback.pushInfo("model : " + str(model.parser_name))
            if model.is_runnable:
                self.feedback.pushDebugInfo("runnable model : " + str(model.parser_name))
                nb_items = len(model.items)
                if model.getNbItems() > 0:
                    indexes = range(nb_items)
                    model.applyItemsWithContext(indexes,self.context,self.feedback)
                else:
                    self.feedback.reportError("Empty model : " + str(model.parser_name))
                
    """ Model update """
    
    def addST(self,item):
        stName = item.getName()
        self.frictionModel.addCol(stName)
        self.fusionModel.setCurrentST(stName)
        
    def removeST(self,name):
        self.frictionModel.removeColFromName(name)
        self.fusionModel.removeSTFromName(name)
        
    def addClass(self,item):
        self.frictionModel.addRowItemFromBase(item)        
        
    def removeClass(self,name):
        self.frictionModel.removeRowFromName(name)
        
    def addGroup(self,item):
        pass
        
    def removeGroup(self,name):
        self.feedback.pushDebugInfo("Removing group from bdModel " + str(name))
        self.classModel.removeFromGroupName(name)
        self.selectionModel.removeFromGroupName(name)
        for st, grp_model in self.fusionModel.st_groups.items():
            grp_model.removeGroupFromName(name)
        
    """ XML functions """
        
    def toXML(self,indent=""):
        xmlStr = indent + "<" + self.parser_name + ">"
        new_indent = indent + " "
        for model in self.models:
            xmlStr += "\n" + indent + model.toXML(indent=new_indent)
        xmlStr += "\n" + indent + "</" + self.parser_name + ">"
        return xmlStr
        
    def getModelFromParserName(self,name):
        for model in self.models:
            if model.parser_name == name:
                return model
        return None
        
    def fromXMLRoot(self,root):
        for child in root:
            utils.debug("tag = " + str(child.tag))
            model = self.getModelFromParserName(child.tag)
            if model:
                model.fromXMLRoot(child)
                model.layoutChanged.emit()
