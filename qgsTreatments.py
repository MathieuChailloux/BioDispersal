
from qgis.core import QgsProcessingFeedback

import sys
import subprocess
#import processing

import utils
import qgsUtils

def applySelection(in_layer,expr,out_layer):
    pass
    
def applyRasterization(in_path,field,out_path):
    utils.debug("applyRasterization")
    in_layer = qgsUtils.loadVectorLayer(in_path)
    extent = in_layer.extent()
    x_min = extent.xMinimum()
    x_max = extent.xMaximum()
    y_min = extent.yMinimum()
    y_max = extent.yMaximum()
    # Create the destination data source
    pixel_size = 25
    NoData_value = -9999
    #x_res = int((x_max - x_min) / pixel_size)
    #y_res = int((y_max - y_min) / pixel_size)
    width = int((x_max - x_min) / pixel_size)
    height = int((y_max - y_min) / pixel_size)
    p = subprocess.Popen(['gdal_rasterize',
                            #'-l','layer_name',
                            '-at',
                            '-a',field,
                            #'-burn','0.0',
                            '-te',str(x_min),str(y_min),str(x_max),str(y_max),
                            #'-tr',str(x_res),str(y_res),
                            '-ts', str(width), str(height),
                            in_path,
                            out_path],
                            stderr=subprocess.PIPE)#, stdout=sys.stdout)#stdin=PIPE, stdout=PIPE, stderr=PIPE)
    out,err = p.communicate()
    utils.debug(str(p.args))
    utils.info(str(out))
    if err:
        utils.user_error(str(err))
        
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
    # p = subprocess.Popen(cmd_args,stderr=subprocess.PIPE,stdout=subprocess.PIPE)
    # out,err = p.communicate()
    # utils.debug(str(p.args))
    # utils.info(str(out))
    # if err:
        # utils.user_error(str(err))
        
        