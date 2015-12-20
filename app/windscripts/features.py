#Defines the feature wrappers and the project wrapper
#We save everyt+hing 
import fiona
from fiona.crs import from_epsg
import rasterio
from rasterio.features import rasterize
import json
import pyproj
import numpy as np
from skimage.graph import route_through_array
from tsp import tsp_ca
from itertools import izip
from shapely.geometry import Point, shape, LineString, mapping
import networkx as nx
import itertools

#Helper functions
# (Lat,Lon)
def createCustomCRS(lat_0,lon_0):
    '''
    This function takes a lat and lon pair
    and returns a Tranverse Mercator CRS
    centered at that pair
    '''
    tmcrs = {u'ellps': u'WGS84',
             u'lat_0': lat_0,
             u'lon_0': lon_0,
             u'no_defs': True,
             u'proj': u'tmerc',
             u'units': u'm'
             }
    return tmcrs
    
def pointTrans(crs,inverse=False):
    proj = pyproj.Proj(crs,preserve_units=True)
    def trans(tpl):
        return proj(tpl[0],tpl[1],inverse=inverse)
    return trans

def customTransform(crs,original,toLatLon=False):
    '''
    Transorms from custom projection to lat,lon
    and viceversa
    crs is a dictionary, original is a geojson-like dict,
    toLatLon: if true will transform to LatLon, otherwise from
    '''
    geometry = original.copy()
    trans = pointTrans(crs,inverse=toLatLon)
    if geometry['type'] == 'Point':
        geometry['coordinates'] = trans(geometry['coordinates'])
    elif geometry['type'] == 'MultiPoint' or geometry['type'] == 'LineString':
        geometry['coordinates'] = map(trans,geometry['coordinates'])
    elif geometry['type'] == 'Polygon' or geometry['type'] == 'MultiLineString':
        elements = []
        for element in geometry['coordinates']:
            elements.append(map(trans,element))
        geometry['coordinates'] = elements
    elif geometry['type'] == 'MultiPolygon':
        elements = []
        for element in geometry['coordinates']:
            subelements = []
            for subelement in element:
                subelements.append(map(trans,subelement))
            elements.append(map(trans, element))
        geometry['coordinates'] = elements
    else:
        raise NameError("Geometry type not supported: " + geometry['type'])
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
    
class GeoFeat(object):
    '''
    Holds the pertinent information and methods for individual
    features. Stores information in WGS84 LatLon coordinates
    '''
    #def __init__(self,interpretation=None,cost=None,name=None, **kwargs):
    #    super(GeoFeat, self).__init__()
    #    if interpretation:
    #        self.interpretation = interpretation
    #    if cost:
    #        self.cost = cost
    #    if name:
    #        self.name = name
    #    self.geojson = {}

    def __str__(self):
        return str(self.geojson)
        
    def read_shapefile(self,filename,properties=None):
        features = []
        with fiona.open(filename) as shp:
            crs = shp.crs
            proj = pyproj.Proj(crs)
            if not proj.is_latlong():
                trans = pointTrans(crs,inverse=True)
                x1,y1 = trans(shp.bounds[:2])
                x2,y2 = trans(shp.bounds[2:])
                self.bounds = (x1,y1,x2,y2)
            else:
                self.bounds = shp.bounds
            for feat in shp:
                feature = feat.copy()
                if not proj.is_latlong():
                    feature['geometry'] = customTransform(shp.crs,feature['geometry'],toLatLon=True)
                features.append(feature)
        self.geojson = {"type": "FeatureCollection","features": features}
        
    def get_projected_gjson(self,crs):
        #missing, place crs in geojson
        features = []
        for feat in self.geojson["features"]:
            feature = feat.copy()
            feature['geometry'] = customTransform(crs,feature['geometry'],toLatLon=False)
            feature['properties'] = feat['properties']
            features.append(feature)
        return {"type": "FeatureCollection","features": features}
        
    def get_costRaster(self,mbb,transform,psize,crs):
        x_min = mbb[0]
        y_min = mbb[1]
        x_max = mbb[2]
        y_max = mbb[3]
        x_res = int((x_max - x_min) / psize)
        y_res = int((y_max - y_min) / psize)
        
        features = self.get_projected_gjson(crs)['features']
        feats = [g['geometry'] for g in features]
        
        raster = rasterize(
            feats,
            out_shape=(y_res, x_res),
            transform=transform,
            dtype='float32',
            all_touched=True)
        
        if self.interpretation == 'boundary':
            #1000 is just an arbitrarily large number, could try np.inf
            raster = np.where(raster==0,1000.0,self.cost)
            print 'at boundary', raster
        elif self.interpretation == 'crossing':
            raster = raster*(self.cost/psize)
            print 'at all else', raster
        return raster
        
        

class CraneProject(object):
    """
    boundary is a feature
    turbines is a feature
    features are a set of features
    """

    #def __init__(self,turbines=None,boundary=None,features=[],psize=50.0, **kwargs):
    #    super(CraneProject, self).__init__()
    #    if boundary:
    #        self.boundary = boundary
    #        self.set_boundary(boundary)
    #    if turbines:
    #        self.turbines=turbines
    #    if features:
    #        self.features = features
    #    if psize:
    #        self.psize = psize
    
    def set_boundary(self,boundary):
        self.boundary = boundary
        self.walkCost = boundary.cost
        self.crs = createCustomCRS(boundary.bounds[1],boundary.bounds[0])
        self.bounds = list(self.reproject(boundary.bounds[:2])) + list(self.reproject(boundary.bounds[2:]))        
    
    def reproject(self, tpl):
        return pointTrans(self.crs)(tpl)
    
    def createCostRaster(self):
        #t= [psize,rotation,topleft-x-coord,rotation,-psize,topleft-y-coord]
        transform = [self.psize,0.0 ,self.bounds[0],0.0,-self.psize,self.bounds[-1]]
        costRaster = self.boundary.get_costRaster(self.bounds,transform,self.psize,self.crs)
        for feature in self.features:
            costRaster += feature.get_costRaster(self.bounds,transform,self.psize,self.crs)
        
        self.transform = transform
        self.costRaster = costRaster
    
    def coord2pixelOffset(self,x,y):
        originX = self.transform[2]
        originY = self.transform[5]
        xOffset = int((x - originX)/self.psize)
        yOffset = int((originY-y)/self.psize)
        return xOffset,yOffset
    
    def pixelOffset2coord(self,xOffset,yOffset):
        originX = self.transform[2]
        originY = self.transform[5]
        coordX = originX+self.psize*xOffset+self.psize/2
        coordY = originY-self.psize*yOffset-self.psize/2
        return coordX, coordY
    
    def shortest_path(self,p1,p2):
        # Based on Dijkstra's minimum cost path algorithm
        start = self.coord2pixelOffset(*p1)[::-1] #We need to reverse them for the route_to_array
        end = self.coord2pixelOffset(*p2)[::-1]
        indices, weight = route_through_array(
            self.costRaster, start,end,geometric=True,fully_connected=True)
        indices = np.array(indices).T
        path = np.zeros_like(self.costRaster)
        path[indices[0], indices[1]] = 1
        return path, weight
    
    def create_nx_graph(self):
        self.siteGraph = nx.Graph()
        self.sitePos = {}
        
        for feat in self.turbines.get_projected_gjson(self.crs)['features']:
            try:
                self.sitePos[feat['id']]= feat['geometry']['coordinates']
            except:
                print 'ERROR when fetching id'
        self.siteGraph.add_nodes_from(self.sitePos.keys())
        for combo in itertools.combinations(self.siteGraph.nodes(),2):
            path, distance = self.shortest_path(self.sitePos[combo[0]],self.sitePos[combo[1]])
            self.siteGraph.add_edge(combo[0],combo[1],weight=distance,pathArray=path)
        return self.siteGraph, self.sitePos
    
    def array2shape(self,pathArray,startCoord, stopCoord):
        #Here we take a raster representation of a path and convert
        #to a Shapely object.
        
        #first convert index list to coordinates
        #NOTE: this might be doable with rasterio in the future
        indeces = np.where(pathArray>0.0)
        coords = [self.pixelOffset2coord(p[1],p[0]) for p in izip(*indeces)]
        line = [startCoord]
        #replace the first one with the startCoord
        p1 = Point(line[-1])
        distances = np.array(map(p1.distance,map(Point,coords)))
        minIndex = np.where(distances==distances.min())[0][0]
        del coords[minIndex]
        
        while coords:
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
            self.solvedGraph[edge[0]][edge[1]]['pathArray'] = self.siteGraph[edge[0]][edge[1]]['pathArray']
            
        return self.solvedGraph
    
    def expandPaths(self):
        #convert paths into geoJson features with proper crossings
        #holy shit
        for edge in self.solvedGraph.edges():
            pathArray = self.solvedGraph[edge[0]][edge[1]]['pathArray']
            path = self.array2shape(pathArray,self.sitePos[edge[0]],self.sitePos[edge[1]])
            i_coords = self.get_inter_coords(path)
            steps = self.split_by_coords(path,i_coords)
            self.solvedGraph[edge[0]][edge[1]]['steps'] = steps
        return self.solvedGraph
    
    def get_inter_coords(self,path):
        """ path is a shapely LineString object """
        #TODO: improve
        i_coords = []
        for feature in self.features:
            if feature.interpretation != 'crossing': continue
            if feature.cost == 0.0: continue
            featureGJSON = feature.get_projected_gjson(self.crs)['features']
            for element in featureGJSON:
                geoType =element['geometry']['type']
                if geoType == 'LineString' or geoType == 'MultiLineString':
                    line = shape(element['geometry'])
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
            return [self.shape2GJSON(path)]
        i_coords = sorted(i_coords, key=path.project,reverse=True)
        thisCoord = i_coords.pop()
        split = path_cut(path,path.project(thisCoord))
        if len(split) == 1:
            return [self.shape2GJSON(thisCoord)]+self.split_by_coords(split[0],i_coords)
        else:
            return [self.shape2GJSON(split[0]),self.shape2GJSON(thisCoord)]+self.split_by_coords(split[1],i_coords)
                
    def shape2GJSON(self,shape):
        gjsoned = {'type':'Feature','geometry':customTransform(self.crs,mapping(shape),toLatLon=True)}
        properties = None
        if gjsoned['geometry']['type'] == 'LineString':
            properties = {
                'cost':self.boundary.cost*shape.length,
                'activity':'CraneWalk',
                'detail':'Regular crane walk'
                }
        elif gjsoned['geometry']['type'] == 'Point':
            properties = shape.spit_properties()
        
        gjsoned['properties'] = properties
        return gjsoned

    def get_geojson(self):
        """
        Returns the Geo JSON to be displayed by Leaflet in the GUI
        """
        sequence = nx.topological_sort(self.solvedGraph)
        schedule = {"type":"FeatureCollection","features":[]}
        order = 0
        trans = pointTrans(self.crs,inverse=True)
        for pair in zip(sequence,sequence[1:]):
            erection = {"type":"Feature","properties":{},"geometry":{}}
            erection["properties"]["activity"] = 'Turbine Erection'
            erection["properties"]["detail"] =  'Turbine: '+ str(pair[0])
            erection["properties"]['cost'] = self.turbines.cost
            erection["properties"]['order'] = order
            order += 1
            erection["geometry"]["coordinates"] = trans(self.sitePos[pair[0]])
            erection["geometry"]["type"] = "Point"
            schedule["features"].append(erection)
            for step in self.solvedGraph[pair[0]][pair[1]]['steps']:
                step['properties']['order'] = order
                order += 1
                schedule["features"].append(step)

        return schedule