#Defines the feature wrappers and the project wrapper
#We save everything 
import fiona
from fiona.crs import from_epsg
import json
import pyproj
import numpy as np
from skimage import route_through_array
from tsp import tsp_ca
from itertools import izip
from shapely import Point, shape

#Helper functions
def to84(tpl,crs):
    proj1=pyproj.Proj(crs,preserve_units=True)
    wgs84=pyproj.Proj("+init=EPSG:4326",preserve_units=True)
    return pyproj.transform(proj1,wgs84,tpl[0],tpl[1])
    
def from84(tpl,crs):
    proj1=pyproj.Proj(crs,preserve_units=True)
    wgs84=pyproj.Proj("+init=EPSG:4326",preserve_units=True)
    return pyproj.transform(wgs84,proj1,tpl[0],tpl[1])
    
    
def transform_wgs84(crs,original,reverse=False):
    geometry = original.copy()
    #TODO: Ugly
    def trans84(tpl):
        if reverse:
            return from84()
        return to84(tpl,crs)
    if geometry['type'] == 'Point':
        geometry['coordinates'] = trans84(geometry['coordinates'])
    elif geometry['type'] == 'MultiPoint' or geometry['type'] == 'LineString':
        geometry['coordinates'] = map(trans84,geometry['coordinates']
    elif geometry['type'] == 'Polygon' or geometry['type'] == 'MultiLineString':
        elements = []
        for element in geometry['coordinates']:
            elements.append(map(trans84,element))
        geometry['coordinates'] = elements
    else:
        raise NameError("Geometry type not supported.")
        return
    return geometry
    
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
            
    
class GPoint(Point):
    activity = None
    cost = None
    detail = None
    
    def spit_properties(self):
        properties = {
            'cost':self.cost,
            'activity':self.activity,
            'detail':self.detail
            }
        return properties
    
class GeoFeat:
    def __init__(self,interpretation=None,cost=None,name=None):
        self.interpretation = interpretation
        self.cost = cost
        self.name = name
    
    def read_shapefile(self,filename):
        features = []
        with fiona.open(shpfile) as shp:
            crs = shp.crs
            x1,y1 = transform84(shp.bounds[:2],crs)
            x2,y2 = transform84(shp.bounds[2:],crs)
            self.bounds = (x1,y1,x2,y2)
            for feat in shp:
                feature = feat.copy()
                feature['geometry'] = transform_wgs84(shp.crs,feature['geometry'])
            if properties: feature['properties'] = properties
                features.append(feature)
        self.geojson = {"type": "FeatureCollection","features": features}
        
    def get_projected_gjson(self,crs):
        #missing, place crs in geojson
        features = []
        for feat in self.geojson["features"]:
            feature = feat.copy()
            feature['geometry'] = transform_wgs84(shp.crs,feature['geometry'],reverse=True)
        if properties: feature['properties'] = properties
            features.append(feature)
        return {"type": "FeatureCollection","features": features}
        
    def get_costRaster(self,mbb,transform,psize,crs):
        x_min = mbb[0]
        y_min = mbb[1]
        x_max = mbb[2]
        y_max = mbb[3]
        x_res = int((x_max - x_min) / psize)
        y_res = int((y_max - y_min) / psize)
        
        features = self.get_projected_gjson(crs)
        feats = [g['geometry'] for g in features]
        
        raster = rasterio.rasterize(
            feats,
            out_shape=(x_res, y+res),
            transform=transform,dtype='float32',
            all_touched=True)
        
        if self.interpretation == 'boundary':
            #1000 is just an arbitrarily large number, could try np.inf
            raster = np.where(raster==0,1000,self.cost)
        elif self.interpretation == 'crossing':
            raster = raster*(self.cost/psize)
        return raster
        
        

class CraneProject:
    def __init__(self,turbines=None,boundary=None,psize=50.0):
        if boundary:
            self.walkCost = boundary.cost
            self.bounds = boundary.bounds
        self.turbines=turbines
        self.boundary=boundary
        self.features = []
        self.psize = 50.0
        self.crs = from_epsg(3857)
    
    def set_boundary(self,boundary):
        if boundary:
            self.bounds = boundary.bounds
            self.walkCost = boundary.walkCost
    
    def createCostRaster(self):
        #t= [psize,rotation,topleft-x-coord,rotation,-psize,topleft-y-coord]
        transform = [self.psize,0.0 ,self.bounds[0],0.0,-self.psize,self.bounds[-1]]
        costRaster = self.boundary.get_costRaster(self.bounds,transform,self.psize)
        for feature in features:
            costRaster += feature.get_costRaster(self.bounds,transfrm,self.psize,self.crs)
        
        self.transform = transform
        self.cost_raster = cost_raster
    
    def coord2pixelOffset(self,x,y):
        originX = self.transform[2]
        originY = self.transform[5]
        xOffset = int((x - originX)/self.psize)
        yOffset = int((y - originY)/self.psize)
        return xOffset,yOffset
    
    def pixelOffset2coord(self,xOffset,yOffset):
        originX = self.transform[2]
        originY = self.transform[5]
        coordX = originX+self.psize*xOffset+self.psize/2
        coordY = originY+self.psize*yOffset+self.psize/2
        return coordX, coordY
    
    def shortest_path(self,p1,p2):
        # Based on Dijkstra's minimum cost path algorithm
        start = self.coord2pixelOffset(*p1)
        end = self.coord2pixelOffset(*p2)
        indices, weight = route_through_array(
            self.costRaster, start,end,geometric=True,fully_connected=True)
        indices = np.array(indices).T
        path = np.zeros_like(self.costRaster)
        path[indices[0], indices[1]] = 1
        return path, weight
    
    def create_nx_graph(self):
        self.siteGraph = nx.Graph()
        self.sitePos = {}
        
        for feat in self.turbines.get_projected_gjson(self.crs)['features']
            try:
                sitePos[feat['id']]= t['geometry']['coordinates']
            except:
                print 'ERROR when reading Shapefile'
                continue
        self.siteGraph.add_nodes_from(sitePos.keys())
        for combo in itertools.combinations(siteGraph.nodes(),2):
            path, distance = self.shortest_path(sitePos[combo[0]],sitePos[combo[1]])
            self.siteGraph.add_edge(combo[0],combo[1],weight=distance,pathArray=path)
        return siteGraph, sitePos
    
    def array2shape(self,pathArray,startCoord, stopCoord):
        #Here we take a raster representation of a path and convert
        #to a Shapely object.
        
        #first convert index list to coordinates
        #NOTE: this might be doable with rasterio in the future
        indeces = np.where(pathArray==1)
        coords = [self.pixelOffset2coord(p[1],p[0]) for p in izip(*indeces)]]
        line = [startCoord]
        #replace the first one with the startCoord
        p1 = Point(line[-1])
        distances = np.array(map(p1.distance,map(Point,coords)))
        minIndex = np.where(distances==distances.min())[0][0]
        del coords[minIndex]
        
        while indeces:
            p1 = Point(line[-1])
            distances = np.array(map(p1.distance,map(Point,coords)))
            minIndex = np.where(distances==distances.min())[0][0]
            line.append(coords[minIndex])
            del coords[minIndex]
        
        #replace last element with endCoord
        del line[-1]
        line.append(stopCoord)
        return shape({'type':'LineString','coordinates':line})
            
    def solve_tsp(self,algo='ca'):
        if algo == 'ca':
            self.solvedGraph = tsp_ca(self.siteGraph)
        
        for edge in self.solvedGraph.edges():
            solution[edge[0]][edge[1]]['pathArray'] = siteGraph[edge[0]][edge[1]]['pathArray']
            
        return self.solvedGraph
    
    def expandPaths(self):
        #convert paths into geoJson features with proper crossings
        #holy shit
        for edge in self.solvedGraph.edges():
            pathArray = self.solvedGraph[edge[0]][edge[1]]['pathArray']
            path = self.array2shape(pathArray,self.sitePos[edge[0]],sitePos[edge[1]])
            i_coords = self.get_inter_coords(path)
            steps = self.split_by_coords(path,i_coords)
            
    
    def get_inter_coords(self,path):
        """ path is a shapely LineString object """
        #TODO: improve
        i_coords = []
        for feature in self.features:
            if feature.interpretation is not 'crossing': continue
            if feature.cost == 0.0: continue
            feats = feature.get_projected_gjson(self.crs)['features']
            for f in feats:
                t =feature['geometry']['type']
                if t == 'LineString' or t == 'MultiLineString':
                    line = shape(feature['geometry'])
                    ints = line.intersection(path)
                    if hasattr(ints, '__iter__'):
                        for each in ints:
                            each = GPoint(each)
                            each.activity = feature.interpretation
                            each.cost = feature.cost
                            each.detail = feature.name
                            i_coords.append(each)
                    else:
                        ints = GPoint(ints)
                        ints.activity = feature.interpretation
                        ints.cost = feature.cost
                        ints.detail = feature.name
                        i_coords.append(ints)
        return i_coords
        
    def split_by_coords(self,path, i_coords):
        #path should be given already as a LineString.
        if not i_coords:
            return [path]
        i_coords = sorted(i_coords, key=path.project,reverse=True)
        thisCoord = i_coords.pop()
        split = path_cut(path,path.project(thisCoord))
        if len(split) == 1:
            return [thisCoord]+split_by_coords(split[0],i_coords)
        else:
            return [split[0],thisCoord]+split_by_coords(split[1],i_coords)
                
    def shape2GJON(self,shape):
        gjsoned = {'geometry':mapping(shape)}
        properties = None
        if gjsoned['geometry']['type'] == 'LineString':
            properties = {
                'cost':self.boundary.cost,
                'activity':'CraneWalk',
                'detail':'Regular crane walk'
                }
        elif gsoned['geometry']['type'] == 'Point':
            properties = shape.spit_properties()
        
        gsoned['properties'] = properties
        return gsoned