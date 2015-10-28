from geopy import *
import pandas as pd

def get_path_cost(geopath,layerDict,walkCost):
    costDetail = {}
    costDetail['total'] =0.0
    costDetail['CraneWalk'] = 0.0
    costDetail['Crossing'] = 0.0
    for step in geopath:
        if step['properties']['activity'] == 'CraneWalk':
            step['properties']['cost'] = step['properties']['length']*walkCost
            costDetail['CraneWalk'] = step['properties']['cost']+costDetail['total']
        elif step['properties']['activity'] == 'Crossing':
            step['properties']['cost'] = layerDict[step['properties']['crossing']]['cc']
            costDetail['Crossing'] = step['properties']['cost']+costDetail['Crossing']
    costDetail['total'] =  costDetail['CraneWalk']+ costDetail['Crossing']
    return costDetail, geopath
    
def get_total_cost(tsp_sol,tpos,layerDict,pathDirectory,CostSurfacefn,walkCost):
    cost = {}
    cost['total'] = 0.0
    cost['CraneWalk'] = 0.0
    cost['Crossing'] = 0.0
    for edge in tsp_sol.edges():
        geograph = shortestPath(CostSurfacefn,pathDirectory+'Path'+edge[0]+'_'+edge[1]+'.shp',tpos[edge[0]],tpos[edge[1]],layerDict)
        costing, geograph = get_path_cost(geograph,layerDict,walkCost)
        tsp_sol.edge[edge[0]][edge[1]]['costing'] = costing
        tsp_sol.edge[edge[0]][edge[1]]['geobj'] = geograph
        tsp_sol.edge[edge[0]][edge[1]]['TotalCost'] = costing['total']
        cost['CraneWalk'] =cost['CraneWalk']+ tsp_sol.edge[edge[0]][edge[1]]['costing']['CraneWalk']
        cost['Crossing'] =cost['Crossing'] +  tsp_sol.edge[edge[0]][edge[1]]['costing']['Crossing']
    cost['total'] = cost['CraneWalk'] + cost['Crossing']
    return cost, tsp_sol

def get_geojson(solution,erectionCost,tpos):
    """
    Coordinates should be in WGS84 for this function to work
    """
    sequence = nx.topological_sort(solution)
    schedule = {"type":"FeatureCollection","features":[]}
    order = 0
    for index in range(len(sequence)):
        erection = {"type":"Feature","properties":{},"geometry":{}}
        erection["properties"]['activity'] = 'Turbine Erection'
        erection["properties"]["detail"] =  'Turbine: '+ str(sequence[index])
        erection["properties"]['cost'] = erectionCost
        erection["properties"]['order'] = order
        order = order + 1
        erection["geometry"]["coordinates"] = list(tpos[str(sequence[index])])
        erection["geometry"]["type"] = "Point"
        schedule["features"].append(erection)
        if index < len(sequence)-1:
            for path in solution[sequence[index]][sequence[index+1]]['geobj']:
                path['properties']['order'] = order
                order = order + 1
                schedule["features"].append(path)


    return schedule