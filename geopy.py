#Based on the GDAL Cookbook
#---Imports---
from osgeo import gdal, osr, ogr
from skimage.graph import route_through_array
import numpy as np
import networkx as nx
import fiona
from fiona.crs import to_string,from_string
from fiona.tool import crs_uri
from gdalconst import *
import copy
import math
import pyproj
import os
import itertools
import shapely
from shapely.geometry import *
from shapely.ops import linemerge
from collections import OrderedDict, Counter
import rasterio


#---Building the Cost Raster---
def get_crs(layerDict):
    crsList = []
    for name in layerDict:
        with fiona.open(layerDict[name]['file']) as s:
            crsList.append(to_string(s.crs))
    return from_string(Counter(crsList).most_common()[0][0])

def get_mbb(layerDict,crs):
    for name in layerDict:
        if 'logic' in layerDict[name] and layerDict[name]['logic'] == 'boundary':
            with fiona.open(layerDict[name]['file']) as s:
                x1, y1, x2, y2 = s.bounds
                if to_string(crs) != to_string(s.crs):
                    proj1=pyproj.Proj(s.crs)
                    proj2=pyproj.Proj(crs,preserve_units=True)
                    minx, miny = pyproj.transform(proj1,proj2,x1,y1)
                    maxx, maxy = pyproj.transform(proj1,proj2,x2,y2)
                    return (minx,miny,maxx,maxy)
                else:
                    return (x1,y1,x2,y2)
        else:
            continue
    raise NameError("No Layer of Type Boundary was provided")

def get_mbb_and_srs(layerDict):
    """Deprecated, please use get_crs and get_mbb"""
    #This function is unsatisfactory, it should actually be two different functions, one for the MBB and one for the SRS. Let's do that.
    for name in layerDict:
        with fiona.open(layerDict[name]['file']) as s:
            if 'minx' not in locals():
                minx, miny, maxx, maxy = s.bounds
                CRS = s.crs
                #very unclean way to get properly formatted SRS
                vector = ogr.GetDriverByName('ESRI Shapefile')
                src_ds = vector.Open(layerDict[name]['file'])
                src_lyr = src_ds.GetLayer(0)
                srs = osr.SpatialReference()
                srs.ImportFromWkt(src_lyr.GetSpatialRef().__str__())
            elif s.crs == CRS:
                x1, y1, x2, y2 = s.bounds
                if x1 < minx: minx = x1
                if y1 < miny: miny = y1
                if x2 > maxx: maxx = x2
                if y2 > maxy: maxy = y2
            else: #raise NameError('Layer: ' + str(name) + ' is of wrong CRS: ' + str(s.crs) + 'desired CRS: ' + str(CRS))
                x1, y1, x2, y2 = s.bounds
                proj1=pyproj.Proj(s.crs)
                proj2=pyproj.Proj(CRS,preserve_units=True)
                x1, y1 = pyproj.transform(proj1,proj2,x1,y1)
                x2, y2 = pyproj.transform(proj1,proj2,x2,y2)
                if x1 < minx: minx = x1
                if y1 < miny: miny = y1
                if x2 > maxx: maxx = x2
                if y2 > maxy: maxy = y2
    return (minx,miny,maxx,maxy),srs

def new_raster(mbb, psize,bands,name,srs,travelDefault=0.0):
    #mbb is the minimum bounding box, of the form (minx,miny,maxx,maxy)
    #psize is pixel size in units of the coordinates
    #bands should be the length of layers to be included
    #Quick definition of the geotransform:
    #x=ax+by+xmin
    #y=dx+ey+ymax
    #geotransform = [xmin, a, b, ymax, d, e]
    #in our case, a, -e = psize and b,d = 0, assuming north face up.

    x_min = mbb[0]
    y_min = mbb[1]
    x_max = mbb[2]
    y_max = mbb[3]
    x_res = int((x_max - x_min) / psize)
    y_res = int((y_max - y_min) / psize)


    #---Using GDAL---
    #target_ds = gdal.GetDriverByName('GTiff').Create(name, x_res, y_res, bands+1, gdal.GDT_Float32)
    #target_ds.SetGeoTransform((x_min, psize, 0, y_max, 0, -psize))
    #target_ds.SetProjection(srs.ExportToWkt())
    #band = target_ds.GetRasterBand(1)
    #band.Fill(travelDefault)

    #---Using Rasterio---
    transform = [x_min, psize,0.0,y_max,0.0,-psize]
    #Will work only if srs is formatted in the PROJ4 style
    print mbb
    with rasterio.open(
        name, 'w',crs=srs,
        driver='GTiff', width=x_res, height=y_res,count=bands,
        transform=transform,
        dtype=rasterio.float32) as s:
        x = np.zeros((x_res,y_res),dtype=np.float32)
        for band in range(bands):
            s.write_band(band+1,x)
    return
    
def burn_layers(layerDict,tiffile):
    i = 2
    target_ds = gdal.Open(tiffile,GA_Update)
    for name in layerDict:
        source_ds = ogr.Open(layerDict[name]['file'])
        source_layer = source_ds.GetLayer()
        #very ugly hack
        if 'logic' in layerDict[name] and layerDict[name]['logic'] == 'boundary':
            gdal.RasterizeLayer(target_ds, [i], source_layer, None, None, burn_values=[layerDict[name]['cost']], options=['ALL_TOUCHED=TRUE'])
            bindex = i-1
            bcost = layerDict[name]['cost']
        else:
            gdal.RasterizeLayer(target_ds, [i], source_layer, None, None, burn_values=[layerDict[name]['cost']], options=['ALL_TOUCHED=TRUE'])
        i= i +1
    #Now we get to summarize the cost at band 1
    #We use the maximum cost of each cell.
    bands = target_ds.ReadAsArray()
    for j in range(len(bands)):
        if j == 0:
            master = bands[j]
        else:
            if 'bindex' in locals() and j == bindex: 
                boundary = bands[j]
                boundary[boundary < bcost] = 9999.0
                master = master + boundary
                continue
            master = np.fmax(master,bands[j])
    target_ds.GetRasterBand(1).WriteArray(master)
    #TODO: This needs urgent redo, such that only travel incurring shapefiles have possibility to add travel cost. 
    target_ds.FlushCache()
    target_ds = None
    return

def get_cell_cost(costDict, cellSize):
    local_dict = copy.deepcopy(costDict)
    for key in local_dict:
        cd = local_dict[key]['cd']
        if 'cc' in local_dict[key]:
            cc = local_dict[key]['cc']/((cellSize/2)*(1.0+math.sqrt(2)))
            local_dict[key]['cost'] = cd + cc
        else: local_dict[key]['cost'] = cd
    return local_dict

def create_cost_raster(filename,layerDict,pSize,travelDefault=None):
    #get aggregated cost
    layerDict = get_cell_cost(layerDict, pSize)
    #get average of our travel cost as default
    if not travelDefault:
        summed = 0
        for name in layerDict:
            summed = summed + layerDict[name]['cd']
        travelDefault = summed/len(layerDict)
    
    #now get me the bounding box and SRS
    #Get preferred SRS
    srs = get_crs(layerDict)
    mbb = get_mbb(layerDict,srs)
    
    #mbb, srs = get_mbb_and_srs(layerDict)
    
    #create the blank raster
    target_ds = new_raster(mbb, pSize,len(layerDict),filename,srs,travelDefault)
    
    #burn layers
    burn_layers(layerDict,filename)
    return 'Created Cost Raster at ' + filename

    
#---Building the Complete Shortest Path Graph---#

def raster2array(rasterfn):
    raster = gdal.Open(rasterfn)
    band = raster.GetRasterBand(1)
    array = band.ReadAsArray()
    return array

def coord2pixelOffset(rasterfn,x,y):
    raster = gdal.Open(rasterfn)
    geotransform = raster.GetGeoTransform()
    originX = geotransform[0]
    originY = geotransform[3]
    pixelWidth = geotransform[1]
    pixelHeight = geotransform[5]
    xOffset = int((x - originX)/pixelWidth)
    yOffset = int((y - originY)/pixelHeight)
    return xOffset,yOffset

def createPath(CostSurfacefn,costSurfaceArray,startCoord,stopCoord,pathValue=255):

    # coordinates to array index
    startCoordX = startCoord[0]
    startCoordY = startCoord[1]
    startIndexX,startIndexY = coord2pixelOffset(CostSurfacefn,startCoordX,startCoordY)

    stopCoordX = stopCoord[0]
    stopCoordY = stopCoord[1]
    stopIndexX,stopIndexY = coord2pixelOffset(CostSurfacefn,stopCoordX,stopCoordY)

    # create path
    indices, weight = route_through_array(costSurfaceArray, (startIndexY,startIndexX), (stopIndexY,stopIndexX),geometric=True,fully_connected=True)
    indices = np.array(indices).T
    path = np.zeros_like(costSurfaceArray)
    path[indices[0], indices[1]] = pathValue
    return path, weight

def array2raster(newRasterfn,rasterfn,array):
    raster = gdal.Open(rasterfn)
    geotransform = raster.GetGeoTransform()
    originX = geotransform[0]
    originY = geotransform[3]
    pixelWidth = geotransform[1]
    pixelHeight = geotransform[5]
    cols = array.shape[1]
    rows = array.shape[0]

    driver = gdal.GetDriverByName('GTiff')
    outRaster = driver.Create(newRasterfn, cols, rows, 1, gdal.GDT_Byte)
    outRaster.SetGeoTransform((originX, pixelWidth, 0, originY, 0, pixelHeight))
    outband = outRaster.GetRasterBand(1)
    outband.WriteArray(array)
    outRasterSRS = osr.SpatialReference()
    outRasterSRS.ImportFromWkt(raster.GetProjectionRef())
    outRaster.SetProjection(outRasterSRS.ExportToWkt())
    outband.FlushCache()
    return

def pixelOffset2coord(rasterfn,xOffset,yOffset):
    raster = gdal.Open(rasterfn)
    geotransform = raster.GetGeoTransform()
    originX = geotransform[0]
    originY = geotransform[3]
    pixelWidth = geotransform[1]
    pixelHeight = geotransform[5]
    coordX = originX+pixelWidth*xOffset+pixelWidth/2
    coordY = originY+pixelHeight*yOffset+pixelHeight/2
    return coordX, coordY
    
def simple_shortest_path(CostSurfacefn,startCoord,stopCoord):

    costSurfaceArray = raster2array(CostSurfacefn) # creates array from cost surface raster

    pathArray, cost = createPath(CostSurfacefn,costSurfaceArray,startCoord,stopCoord) # creates path array
    
    return cost
    
def array2shp(array,outSHPfn,rasterfn,pixelValue):

    # max distance between points
    raster = gdal.Open(rasterfn)
    geotransform = raster.GetGeoTransform()
    pixelWidth = geotransform[1]
    maxDistance = math.ceil(math.sqrt(2*pixelWidth*pixelWidth))
    # maxDistance

    # array2dict
    count = 0
    roadList = np.where(array == pixelValue)
    multipoint = ogr.Geometry(ogr.wkbMultiLineString)
    pointDict = {}
    for indexY in roadList[0]:
        indexX = roadList[1][count]
        Xcoord, Ycoord = pixelOffset2coord(rasterfn,indexX,indexY)
        pointDict[count] = (Xcoord, Ycoord)
        count += 1

    # dict2wkbMultiLineString
    multiline = ogr.Geometry(ogr.wkbMultiLineString)
    for i in itertools.combinations(pointDict.values(), 2):
        point1 = ogr.Geometry(ogr.wkbPoint)
        point1.AddPoint(i[0][0],i[0][1])
        point2 = ogr.Geometry(ogr.wkbPoint)
        point2.AddPoint(i[1][0],i[1][1])

        distance = point1.Distance(point2)

        if distance < maxDistance:
            line = ogr.Geometry(ogr.wkbLineString)
            line.AddPoint(i[0][0],i[0][1])
            line.AddPoint(i[1][0],i[1][1])
            multiline.AddGeometry(line)

    # wkbMultiLineString2shp
    shpDriver = ogr.GetDriverByName("ESRI Shapefile")
    if os.path.exists(outSHPfn):
        shpDriver.DeleteDataSource(outSHPfn)
    outDataSource = shpDriver.CreateDataSource(outSHPfn)
    outLayer = outDataSource.CreateLayer(outSHPfn, geom_type=ogr.wkbMultiLineString )
    featureDefn = outLayer.GetLayerDefn()
    outFeature = ogr.Feature(featureDefn)
    outFeature.SetGeometry(multiline)
    outLayer.CreateFeature(outFeature)
    return

def path_cut(line, distance):
    # Cuts a line in two at a distance from its starting point
    if distance <= 0.0 or distance >= line.length:
        #print distance, line.length
        return [LineString(line)]
    try:
        coords = list(line.coords)
    except Exception:
        print line
    for i, p in enumerate(coords):
        pd = line.project(Point(p))
        if pd == distance:
            return [
                LineString(coords[:i+1]),
                LineString(coords[i:])]
        if pd > distance:
            cp = line.interpolate(distance)
            return [
                LineString(coords[:i] + [(cp.x, cp.y)]),
                LineString([(cp.x, cp.y)] + coords[i:])]

def split_by_coords(path, i_coords):
    #path should be given already as a LineString.
    if not i_coords:
        return [path]
    for i in i_coords:
        i_coords[i]['distance'] = path.project(Point(i_coords[i]['coord']))
    i_coords = OrderedDict(sorted(i_coords.items(), key=lambda t: t[1]['distance']))
    thisCoord = i_coords.popitem()[1]
    split = path_cut(path,thisCoord['distance'])
    if len(split) == 1:
        return [thisCoord]+split_by_coords(split[0],i_coords)
    else:
        return [split[0],thisCoord]+split_by_coords(split[1],i_coords)

def get_inter_coords(path, layerDict):
    i_coords = {}
    i=0
    for key in layerDict:
        if 'logic' in layerDict[key] and layerDict[key]['logic'] == 'boundary': continue
        if layerDict[key]['cc'] == 0.0: continue
        with fiona.open(layerDict[key]['file']) as f:
            for feature in f:
                if feature['geometry']['type'] == 'LineString':
                    line = LineString(feature['geometry']['coordinates'])
                    ints = line.intersection(path)
                    if hasattr(ints, '__iter__'):
                        for each in ints:
                            i_coords[i] = {'coord':each,'type':key,'cost':layerDict[key]['cc']}
                            i = i+1
                    else:
                        i_coords[i] = {'coord':ints.coords[0],'type':key,'cost':layerDict[key]['cc']}
                        i = i+1
    return i_coords

def shp2LS(outputPathfn,startCoord,stopCoord):
    #TODO: A great deal of this step is dealing with the nonesense of 
    #Multilinestrings, which themselves are by-product of the Shapefile creations
    #a next improvement will be to avoid going through the Multilinestrings/SHP step
    with fiona.open(outputPathfn) as path:
        ls = []
        for p in path:
            #TODO: fix NoneType
            if p['geometry'] is not None:
                for pair in p['geometry']['coordinates']:
                    ls.append(pair)
            else: print "NoneType geometry Found!"
    graph = nx.Graph(ls)
    start = None
    minstart = 100000.0
    minstop = 100000.0
    stop = None
    for node in graph.nodes():
        dstart = Point(startCoord).distance(Point(node))
        dstop = Point(stopCoord).distance(Point(node))
        if dstart < minstart:
            minstart = dstart
            start = node
        if dstop < minstop:
            minstop = dstop
            stop = node
    graph.add_edge(startCoord,start)
    graph.add_edge(stopCoord,stop)

    path = nx.shortest_path(graph,source=startCoord, target=stopCoord)

    myLine = LineString(path)
    assert isinstance(myLine, LineString)
    return myLine

def transform_to_wgs84(crs,original):
    geojson = original.copy()
    def trans84(tpl):
        proj1=pyproj.Proj(crs,preserve_units=True)
        wgs84=pyproj.Proj("+init=EPSG:4326",preserve_units=True)
        return pyproj.transform(proj1,wgs84,tpl[0],tpl[1])
    if geojson['type'] == 'Point':
        geojson['coordinates'] = trans84(geojson['coordinates'])
    elif geojson['type'] == 'Polygon':
        elements = []
        for element in geojson['coordinates']:
            elements.append(map(trans84,element))
        geojson['coordinates'] = elements
    else:
        geojson['coordinates'] = tuple(map(trans84,geojson['coordinates']))
    return geojson
# Another Option is to use nx.DiGraph() and allow for easy reversal. Let's see.
def geopack(pathArray,crs):
    geopath = []
    i = 0
    for step in pathArray:
        geobj = {}
        geobj['type'] = 'Feature'
        #NOTE: WE ARE NOT SPECIFYING THE CRS BECAUSE FOR GEOJSON IT IS IMPLIED
        #THAT YOU ARE USING WGS84
        geobj['properties'] = {}
        if type(step) is dict:
            geobj['properties']['activity'] = 'Crossing'
            geobj['geometry'] = transform_to_wgs84(crs,mapping(Point(step['coord'])))
            geobj['properties']['crossing'] = step['type']
            geobj['properties']['detail'] = 'Crossed layer: ' + step['type']
            
        elif step.geom_type == 'LineString':
            geobj['properties']['length'] = step.length
            geobj['properties']['activity'] = 'CraneWalk'
            geobj['geometry'] = transform_to_wgs84(crs,mapping(step))
            geobj['properties']['detail'] = 'Regular crane movement'
        
        geobj['properties']['order'] = i
        geopath.append(geobj)
        i=i+1
    return geopath

def shortestPath(CostSurfacefn,outputPathfn,startCoord,stopCoord,layerDict):

    costSurfaceArray = raster2array(CostSurfacefn) # creates array from cost surface raster

    pathArray, cost = createPath(CostSurfacefn,costSurfaceArray,startCoord,stopCoord) # creates path array
    
    array2shp(pathArray,outputPathfn,CostSurfacefn,255) #converts path array to shp
    
    path = shp2LS(outputPathfn,startCoord,stopCoord)
    
    i_coords = get_inter_coords(path, layerDict)
    
    geopath = split_by_coords(path,i_coords)
    
    with fiona.open(layerDict[layerDict.keys()[0]]['file']) as f:
        crs = f.crs
    
    pathGraph = geopack(geopath,crs)
    
    return pathGraph
    
def create_nx_graph(turbinesfn,tiffile,directory,layerDict):
    #tiffile and turbinesfn should have COMPLETE directory.
    with fiona.open(layerDict.iteritems().next()[1]['file']) as sample:
        crs = sample.crs
    siteGraph = nx.Graph()
    sitePos = {}
    i = 0
    with fiona.open(turbinesfn) as turbines:
        if turbines.crs != crs:
            proj1=pyproj.Proj(turbines.crs,preserve_units=True)
            proj2=pyproj.Proj(crs,preserve_units=True)
            def conversion(x,y):
                return pyproj.transform(proj1,proj2,x,y)
        else:
            def conversion(x,y):
                return (x,y)
        
        sitePos = {}
        for i,t in enumerate(turbines): 
            try:
                sitePos[t['id']]= t['geometry']['coordinates']
            except:
                print 'ERROR when reading Shapefile'
                continue
        siteGraph.add_nodes_from(sitePos.keys())
        for combo in itertools.combinations(siteGraph.nodes(),2):
            distance = simple_shortest_path(tiffile,sitePos[combo[0]],sitePos[combo[1]])
            siteGraph.add_edge(combo[0],combo[1],weight=distance)
    return siteGraph, sitePos

def shp2geojson(shpfile,properties=None):
    features = []
    with fiona.open(shpfile) as shp:
        crs = shp.crs
        for feat in shp:
            feature = feat.copy()
            feature['geometry'] = transform_to_wgs84(shp.crs,feature['geometry'])
            if properties: feature['properties'] = properties
            features.append(feature)
    gjson =  {"type": "FeatureCollection","features": features}
    return gjson