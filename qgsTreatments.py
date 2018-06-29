
from qgis.core import QgsProcessingFeedback, QgsProject

import sys
import subprocess
import processing

import utils
import qgsUtils

nodata_val = '-9999'

def applySelection(in_layer,expr,out_layer):
    pass
    
def applyRasterization(in_path,field,out_path,resolution=None,extent_path=None,load_flag=False):
    utils.debug("applyRasterization")
    in_layer = qgsUtils.loadVectorLayer(in_path)
    if extent_path:
        extent_layer = qgsUtils.loadVectorLayer(extent_path)
        extent = extent_layer.extent()
    else:
        in_layer = qgsUtils.loadVectorLayer(in_path)
        extent = in_layer.extent()
    x_min = extent.xMinimum()
    x_max = extent.xMaximum()
    y_min = extent.yMinimum()
    y_max = extent.yMaximum()
    if not resolution:
        utils.warn("Setting rasterization resolution to 25")
        resolution = 25
    #NoData_value = -9999
    width = int((x_max - x_min) / float(resolution))
    height = int((y_max - y_min) / float(resolution))
    parameters = ['gdal_rasterize',
                  #'-l','tmp_layer',
                  '-at',
                  '-te',str(x_min),str(y_min),str(x_max),str(y_max),
                  '-ts', str(width), str(height),
                  '-ot','Int16',
                  '-of','GTiff',
                  '-a_nodata',nodata_val]
    if field == "geom":
        parameters += ['-burn', '1']
    else:
        parameters += ['-a',field]
    #parameters += ['-ot','Int32']
    #parameters += ['-of','GTiff']
    parameters += [in_path,out_path]
    p = subprocess.Popen(parameters,stderr=subprocess.PIPE)
    # p = subprocess.Popen(['gdal_rasterize',
                            # '-l','layer_name',
                            # '-at',
                            # '-a',field,
                            # '-burn','0.0',
                            # '-te',str(x_min),str(y_min),str(x_max),str(y_max),
                            # '-tr',str(x_res),str(y_res),
                            # '-ts', str(width), str(height),
                            # in_path,
                            # out_path],
                            # stderr=subprocess.PIPE)#, stdout=sys.stdout)#stdin=PIPE, stdout=PIPE, stderr=PIPE)
    out,err = p.communicate()
    utils.debug(str(p.args))
    utils.info(str(out))
    if err:
        utils.user_error(str(err))
    elif load_flag:
        res_layer = qgsUtils.loadRasterLayer(out_path)
        QgsProject.instance().addMapLayer(res_layer)
        
def applyReclassProcessing(in_path,out_path,rules_file,title):
    parameters = {'input' : in_path,
                  'output' : out_path,
                  'rules' : rules_file,
                  'title' : title,
                   'GRASS_REGION_CELLSIZE_PARAMETER' : 50,
                   'GRASS_SNAP_TOLERANCE_PARAMETER' : -1,
                   'GRASS_MIN_AREA_PARAMETER' : 0}
    feedback = QgsProcessingFeedback()
    try:
        processing.run("grass7:r.reclass",parameters,feedback=feedback)
        utils.debug ("call to r.cost successful")
    except Exception as e:
        utils.warn ("Failed to call r.reclass : " + str(e))
        raise e
    finally:
        utils.debug("End runCost")
        
def applyReclassGdal(in_path,out_path,reclass_dict):
    utils.debug("qgsTreatments.applyReclassGdal")
    cmd_args = ['gdal_calc.bat',
                '-A', in_path,
                '--outfile='+out_path]
    expr = '--calc='
    for old_cls,new_cls in reclass_dict.items():
        if expr != '--calc=':
            expr += '+'
        expr += str(new_cls) + '*(A==' + str(old_cls)+ ')'
    cmd_args.append(expr)
    utils.executeCmd(cmd_args)
    res_layer = qgsUtils.loadRasterLayer(out_path)
    QgsProject.instance().addMapLayer(res_layer)
    # p = subprocess.Popen(cmd_args,stderr=subprocess.PIPE,stdout=subprocess.PIPE)
    # out,err = p.communicate()
    # utils.debug(str(p.args))
    # utils.info(str(out))
    # if err:
        # utils.user_error(str(err))
        
def applyRCost(start_path,cost_path,cost,out_path):
        utils.debug ("applyRCost")
        utils.checkFileExists(start_path,"Dispersion Start Layer ")
        utils.checkFileExists(cost_path,"Dispersion Permeability Raster ")
        parameters = { 'input' : cost_path,
                        'start_raster' : start_path,
                        'max_cost' : int(cost),
                        'output' : out_path,
                        #'start_coordinates' : '0,0',
                        #'stop_coordinates' : '0,0',
                        #'outdir' : 'D:\MChailloux\PNRHL_QGIS\tmpLayer_movements.tif',
                        #'nearest' : 'D:\MChailloux\PNRHL_QGIS\tmpLayer_nearest.tif',
                        #'start_points' :  None,
                        #'stop_points' : None,
                        'null_cost' : None,
                        'memory' : 5000,
                        'GRASS_REGION_CELLSIZE_PARAMETER' : 25,
                        'GRASS_SNAP_TOLERANCE_PARAMETER' : -1,
                        'GRASS_MIN_AREA_PARAMETER' : 0,
                        '-k' : False,
                        '-n' : True,
                        '-r' : True,
                        '-i' : False,
                        '-b' : False}
        feedback = QgsProcessingFeedback()
        utils.debug("parameters : " + str(parameters))
        try:
            processing.run("grass7:r.cost",parameters,feedback=feedback)
            print ("call to r.cost successful")
            res_layer = qgsUtils.loadRasterLayer(out_path)
            QgsProject.instance().addMapLayer(res_layer)
        except Exception as e:
            print ("Failed to call r.cost : " + str(e))
            raise e
        finally:  
            utils.debug("End runCost")
        
        