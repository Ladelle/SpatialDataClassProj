import csv
import glob
import json
import os
import sys
import rtree 
import geojson
import networkx as nx
import matplotlib.pyplot as plt
import gdal
import geopandas as gpd
from flask import Flask,  url_for
from flask import request
from flask import jsonify
from flask_cors import CORS
from flask import send_file
from geojson import Point
from geojson import Polygon
from geojson import LineString
from geojson import MultiLineString
from misc_functions import haversine, bearing
import glob
from scipy.spatial import KDTree # added this 10/18/2020
from misc_functions import haversine, bearing

app = Flask(__name__)
CORS(app)

# 
#       $$\            $$\               
#       $$ |           $$ |              
#  $$$$$$$ | $$$$$$\ $$$$$$\    $$$$$$\  
# $$  __$$ | \____$$\_$$  _|   \____$$\ 
# $$ /  $$ | $$$$$$$ | $$ |     $$$$$$$ |
# $$ |  $$ |$$  __$$ | $$ |$$\ $$  __$$ |
# \$$$$$$$ |\$$$$$$$ | \$$$$  |\$$$$$$$ |
#  \_______| \_______|  \____/  \_______|                               
# 

base_path = '5443-Spatial-DS-Augustine/Assignments/A04/assets/api/data'

def isJson(data):
    """
    Helper method to test if val can be json 
    without throwing an actual error.
    """
    try:
        json.loads(data)
        return True
    except ValueError:
        return False

def load_data(path):
    """Given a path, load the file and handle it based on its extension type. 
    """

    _, ftype = os.path.splitext(path) #get fname and extension

    if os.path.isfile(path):
        with open(path) as f:

            if ftype == ".json" :    #handle json
                data = json.load(f)
                # print(data)
                return data


            elif ftype == ".csv":   #handle csv with csv reader
                with open(path, newline ='') as csvfile:
                    data = csv.DictReader(csvfile)
                    return list(data)

            elif ftype == ".geojson":
                data = json.load(f)
            
                return data

            else:
                print("neither json or csv")
                return None


#  ██╗  ██╗██████╗ ████████╗██████╗ ███████╗███████╗███████╗                                                                                                                                  
#  ██║ ██╔╝██╔══██╗╚══██╔══╝██╔══██╗██╔════╝██╔════╝██╔════╝                                                                                                                                  
#  █████╔╝ ██║  ██║   ██║   ██████╔╝█████╗  █████╗  █████╗█████╗█████╗█████╗█████╗█████╗█████╗█████╗█████╗█████╗█████╗█████╗█████╗█████╗█████╗█████╗█████╗█████╗█████╗█████╗█████╗█████╗█████╗
#  ██╔═██╗ ██║  ██║   ██║   ██╔══██╗██╔══╝  ██╔══╝  ██╔══╝╚════╝╚════╝╚════╝╚════╝╚════╝╚════╝╚════╝╚════╝╚════╝╚════╝╚════╝╚════╝╚════╝╚════╝╚════╝╚════╝╚════╝╚════╝╚════╝╚════╝╚════╝╚════╝
#  ██║  ██╗██████╔╝   ██║   ██║  ██║███████╗███████╗███████╗                                                                                                                                  
#  ╚═╝  ╚═╝╚═════╝    ╚═╝   ╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝                                                                                                                                  
                                                                                                                                                                                            
def getTree():
    coords = []
 
    for feature in UFO['features']:
        if type(feature['geometry']['coordinates'][0]) !=float or type(feature['geometry']['coordinates'][1]) !=float:
            pass
        else:
            coords.append(feature['geometry']['coordinates'])

    tree = KDTree(coords)
    print("This is tree: ",tree)
    return tree, coords


# ██████╗ ████████╗██████╗ ███████╗███████╗
# ██╔══██╗╚══██╔══╝██╔══██╗██╔════╝██╔════╝
# ██████╔╝   ██║   ██████╔╝█████╗  █████╗  
# ██╔══██╗   ██║   ██╔══██╗██╔══╝  ██╔══╝  
# ██║  ██║   ██║   ██║  ██║███████╗███████╗
# ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚══════╝

def getRTree():
    idx = rtree.index.Index()
    left,bottom,right,top = (-180,-90,180,90)

    index = 0
    rtreeID= {}
    for feature in UFO['features']:

        if type(feature['geometry']['coordinates'][0]) !=float or type(feature['geometry']['coordinates'][1]) !=float:
            pass
        else:
            left = feature['geometry']['coordinates'][0]
            right = feature['geometry']['coordinates'][0]
            bottom = feature['geometry']['coordinates'][1]
            top = feature['geometry']['coordinates'][1]
            coords = (left,bottom,right,top)
            idx.insert(index,coords)
            rtreeID[index] = feature
            index+=1



    return(idx, rtreeID)                                 

# ██████╗  ██████╗ ██╗   ██╗████████╗███████╗███████╗
# ██╔══██╗██╔═══██╗██║   ██║╚══██╔══╝██╔════╝██╔════╝
# ██████╔╝██║   ██║██║   ██║   ██║   █████╗  ███████╗
# ██╔══██╗██║   ██║██║   ██║   ██║   ██╔══╝  ╚════██║
# ██║  ██║╚██████╔╝╚██████╔╝   ██║   ███████╗███████║
# ╚═╝  ╚═╝ ╚═════╝  ╚═════╝    ╚═╝   ╚══════╝╚══════╝
#  result_feature ={
#     'type': 'FeatureCollection',
#     'features':[],
# }                                                  

# Render the map
@app.route('/token', methods=['GET'])
def index():
    with open ('/Users/Delly/Desktop/NewEnv/mapboxtoken.txt', 'r') as f:
        mapbox_access_token = f.read()

    return mapbox_access_token


@app.route("/", methods=["GET"])
def getRoutes():
    """ getRoutes: this gets all the routes!
    """
    routes = {}
    for r in app.url_map._rules:
        # print(r)
        routes[r.rule] = {}
        routes[r.rule]["functionName"] = r.endpoint
        routes[r.rule]["help"] = formatHelp(r.endpoint)
        routes[r.rule]["methods"] = list(r.methods)

    routes.pop("/static/<path:filename>")
    routes.pop("/")

    response = json.dumps(routes,indent=4,sort_keys=True)
    response = response.replace("\n","<br>")
    return "<pre>"+response+"</pre>"

@app.route("/dataset", methods=["GET"])
def getdataset(): # want to take in data and feature types 
    """
    This Functions takes in a string argument of the dataset
    the user would like to use and places it in a list to check which
    dataset to use.
    example: http://localhost:7878/dataset?data=<dataname>
    """
    results2 = request.args.get('data', None)

    results =[results2]
    print(results)
    

    if 'UFO' == results2:
        sid = 1
        result = UFO # result = UFO is what originally was here
    elif 'MILBASE' == results2:
        sid = 2
        result = MILBASE
    elif 'STATES_BBOXS'== results2:
        sid = 3
        result = STATES_BBOXS
    elif 'STATES'==  results2:
        sid = 4
        result = STATES
    elif 'RROADS' == results2:
        sid = 4
        result = RROADS
    # elif 'VOLC' == results2:
    #     sid = 6
    #     result = VOLC
    elif 'CITIES' == results2:
        sid = 5
        result = CITIES
    else:
        return "None"

    return handle_response(result,sid)

# # setting list og names for front end
# @app.route("/setlist", methods=["GET"])
# def getSetList():
#     """Sends a list of setnames to the front end
#     Params:
#         None
#     Example: http://localhost:8080/setlist
#     """
#     global setNames
#     return handle_response(setNames)
@app.route("/setlist", methods=["GET"])
def getSetList():
    """Sends a list of setnames to the front end
    Params:
        None
    Example: http://localhost:7878/setlist
    """
    global setNames
    nameList = {}
    for name, i in zip(setNames,range(len(setNames))):
        nameList[name] = i
    print(nameList)
    return handle_response(nameList)
    
sid = -1
result_feature ={
    'type': 'FeatureCollection',
    'features':[],
}


# ██████╗  ██████╗ ██╗███╗   ██╗████████╗    ███████╗ █████╗ ██╗   ██╗███████╗██████╗ 
# ██╔══██╗██╔═══██╗██║████╗  ██║╚══██╔══╝    ██╔════╝██╔══██╗██║   ██║██╔════╝██╔══██╗
# ██████╔╝██║   ██║██║██╔██╗ ██║   ██║       ███████╗███████║██║   ██║█████╗  ██║  ██║
# ██╔═══╝ ██║   ██║██║██║╚██╗██║   ██║       ╚════██║██╔══██║╚██╗ ██╔╝██╔══╝  ██║  ██║
# ██║     ╚██████╔╝██║██║ ╚████║   ██║       ███████║██║  ██║ ╚████╔╝ ███████╗██████╔╝
# ╚═╝      ╚═════╝ ╚═╝╚═╝  ╚═══╝   ╚═╝       ╚══════╝╚═╝  ╚═╝  ╚═══╝  ╚══════╝╚═════╝ 


@app.route('/pointSaved')
def pointSaved():
    """
    Saves The points where the lon lat was called into feautre collection
    Example: http://localhost:7878/pointSaved?lon=-82.1888889&lat=36.595
    """
    global sid, result_feature
    
    sid +=1
    lon = float(request.args.get('lon',None))
    lat = float(request.args.get('lat',None))
    # num = int(request.args.get('num',None))
    result_feature['features'].append({
        'type':'Feature',
        'geometry': {
            'type': 'Point',
            'coordinates': [lon, lat]
        },
        'properties': {
            'id': str(sid)
        }
    })
    return (str(sid))  #saves the source id # and returns it

#      ██╗███████╗ ██████╗ ███╗   ██╗    ███████╗ █████╗ ██╗   ██╗███████╗██████╗     ███████╗██████╗  ██████╗ ███╗   ██╗████████╗    ███████╗███╗   ██╗██████╗     ██╗███╗   ██╗███████╗ ██████╗ 
#      ██║██╔════╝██╔═══██╗████╗  ██║    ██╔════╝██╔══██╗██║   ██║██╔════╝██╔══██╗    ██╔════╝██╔══██╗██╔═══██╗████╗  ██║╚══██╔══╝    ██╔════╝████╗  ██║██╔══██╗    ██║████╗  ██║██╔════╝██╔═══██╗
#      ██║███████╗██║   ██║██╔██╗ ██║    ███████╗███████║██║   ██║█████╗  ██║  ██║    █████╗  ██████╔╝██║   ██║██╔██╗ ██║   ██║       █████╗  ██╔██╗ ██║██║  ██║    ██║██╔██╗ ██║█████╗  ██║   ██║
# ██   ██║╚════██║██║   ██║██║╚██╗██║    ╚════██║██╔══██║╚██╗ ██╔╝██╔══╝  ██║  ██║    ██╔══╝  ██╔══██╗██║   ██║██║╚██╗██║   ██║       ██╔══╝  ██║╚██╗██║██║  ██║    ██║██║╚██╗██║██╔══╝  ██║   ██║
# ╚█████╔╝███████║╚██████╔╝██║ ╚████║    ███████║██║  ██║ ╚████╔╝ ███████╗██████╔╝    ██║     ██║  ██║╚██████╔╝██║ ╚████║   ██║       ███████╗██║ ╚████║██████╔╝    ██║██║ ╚████║██║     ╚██████╔╝
#  ╚════╝ ╚══════╝ ╚═════╝ ╚═╝  ╚═══╝    ╚══════╝╚═╝  ╚═╝  ╚═══╝  ╚══════╝╚═════╝     ╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝       ╚══════╝╚═╝  ╚═══╝╚═════╝     ╚═╝╚═╝  ╚═══╝╚═╝      ╚═════╝ 
                                                                                                                                                                                                
"""
THIS FILE HAS INFO FRON FRONT END SAVED TO JSON FILE
"""
@app.route('/jsonSavedFront')
def jsonSavedFront():
    with open('/Users/Delly/Desktop/NewEnv/5443-Spatial-DS-Augustine/Assignments/A04/assets/api/data/mapPoints.geojson','w') as out:
        json.dump(result_feature, out, indent = "   ")
    

    return "DONE"


# ██████╗  ██████╗ ██╗███╗   ██╗████████╗███████╗    ███████╗██████╗  █████╗ ███████╗███████╗██████╗ 
# ██╔══██╗██╔═══██╗██║████╗  ██║╚══██╔══╝██╔════╝    ██╔════╝██╔══██╗██╔══██╗██╔════╝██╔════╝██╔══██╗
# ██████╔╝██║   ██║██║██╔██╗ ██║   ██║   ███████╗    █████╗  ██████╔╝███████║███████╗█████╗  ██║  ██║
# ██╔═══╝ ██║   ██║██║██║╚██╗██║   ██║   ╚════██║    ██╔══╝  ██╔══██╗██╔══██║╚════██║██╔══╝  ██║  ██║
# ██║     ╚██████╔╝██║██║ ╚████║   ██║   ███████║    ███████╗██║  ██║██║  ██║███████║███████╗██████╔╝
# ╚═╝      ╚═════╝ ╚═╝╚═╝  ╚═══╝   ╚═╝   ╚══════╝    ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚══════╝╚═════╝ 
                                                                                                   
@app.route('/pointErased')
def pointErased():
    global sid, result_feature
    sid = -1
    coordinatesNum = len(result_feature['features'])
    coordsErasedFromFile = result_feature['features']
    result_feature['feature'] = []
    print("coordinate #:",coordinatesNum,"coords erased:", coordsErasedFromFile)
    return jsonify(coordinatesNum,coordsErasedFromFile)

"""
VIDEO PART 2: STATES
Dr. Griffin : https://www.youtube.com/watch?v=WX9OBH8Zv0M

"""
@app.route('/states', methods=["GET"])
def states():
    """ Description: returns a list of us states names
        Params: 
            None
        Example: http://localhost:7878/states?filter= 
        This will get all states that starts with tex 
        creates a results list loops through states then creates
        results. it will search from the beginning of list up to the 
        lenght of the text that passing in. if get match then 
        result . append state. if dont have filter then returns all states. 
    """
    filter = request.args.get('filter',None) 
    
    if filter:
        results2 = []
        for state in STATES2:
            if filter.lower() == state['name'][:len(filter)].lower():
                results2.append(state)
    else:
        results2 = STATES2
    return handle_response2(results2)

@app.route('/state_bbox', methods=["GET"])
def state_bbox():
    """
    Description: return a bounding box for a us state
    Params: None
    Example: http://localhost:7878/state_bbox?state=<statename>
    """
    
    state = request.args.get('state',None)
    print(f'STATE {state}')
   
    if not state:
        results = STATES_BBOXS
        return handle_response(results,'')
    results = []
    state = state.lower()

    print(results)

    for row in STATES_BBOXS:

        if row ['name'].lower() == state or row['abbr'].lower() == state:
            row['xmax'] = float(row['xmax'])
            row['xmin'] = float(row['xmin'])
            row['ymin'] = float(row['ymin'])
            row['ymax'] = float(row['ymax'])
            results = row
            print(results)
    return handle_response2(results,None)    




# # ███╗   ██╗███████╗ █████╗ ██████╗ ███████╗███████╗████████╗    ███╗   ██╗███████╗██╗ ██████╗ ██╗  ██╗██████╗  ██████╗ ██████╗      ██████╗ ██████╗ ██████╗ ███████╗
# # ████╗  ██║██╔════╝██╔══██╗██╔══██╗██╔════╝██╔════╝╚══██╔══╝    ████╗  ██║██╔════╝██║██╔════╝ ██║  ██║██╔══██╗██╔═══██╗██╔══██╗    ██╔════╝██╔═══██╗██╔══██╗██╔════╝
# # ██╔██╗ ██║█████╗  ███████║██████╔╝█████╗  ███████╗   ██║       ██╔██╗ ██║█████╗  ██║██║  ███╗███████║██████╔╝██║   ██║██████╔╝    ██║     ██║   ██║██║  ██║█████╗  
# # ██║╚██╗██║██╔══╝  ██╔══██║██╔══██╗██╔══╝  ╚════██║   ██║       ██║╚██╗██║██╔══╝  ██║██║   ██║██╔══██║██╔══██╗██║   ██║██╔══██╗    ██║     ██║   ██║██║  ██║██╔══╝  
# # ██║ ╚████║███████╗██║  ██║██║  ██║███████╗███████║   ██║       ██║ ╚████║███████╗██║╚██████╔╝██║  ██║██████╔╝╚██████╔╝██║  ██║    ╚██████╗╚██████╔╝██████╔╝███████╗
# # ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚══════╝   ╚═╝       ╚═╝  ╚═══╝╚══════╝╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═════╝  ╚═════╝ ╚═╝  ╚═╝     ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝
                                                                                                                                                                   
# """
# GETS THE NEAREST NEIGHBORS 
# """

nearNum = -1
neighborsFeatures = {
    'type':'FeatureCollection',
    'features':[]
}



@app.route('/neighbor', methods = ["GET"])
def findNearestNeigbors():
    """ Description: Return x nearest neigbhors for give lon lat coords
        Params: 
            None
        Example: http://localhost:7878/neighbor?lon=<longitude>&lat=<latitude>&num=<number of nearest neighbors to find>
        http://localhost:7878/neighbor?lon=-2.916667&lat=53.2&num=10
    """
    global tree 
    global coords
    global nearNum
    global neighbors
    global sid
   
    
    nearNum += 1

    lon = float(request.args.get('lon',None))
    lat = float(request.args.get('lat',None))
    num = int(request.args.get('num',None))
    sid += 1
    searchCoords=[lon,lat]     #[[98.581081, 29.38421],[98.581081, 29.38421]]

    
    # returns an array of distances and an array of indices for nearest neighbors
    distanceList, neighborList = tree.query(searchCoords,k=num,distance_upper_bound=180)
    
    # prints the results of the query to the console
   # prints the results of the query to the console
    if num > 1:
        for i in range(0,len(distanceList)):
            print(f"\nLng, Lat: {lon}, {lat}\nNearest neighbor: {coords[neighborList[i]]}\tDistance: {distanceList[i]}")
           
    else:
            print(f"\nLng, Lat: {lon}, {lat}\nNearest neighbor: {neighborList}\tDistance: {distanceList}")
     
   
    neighbors = []
  
    if num == 1:
        point = geojson.Point(coords[0])
        neighbors.append(geojson.Feature(geometry=point )) 
    else:
        for i in neighborList:
            # neighbors.append(coords[i])
    # neighbors = geojson.FeatureCollection(neighbors)
           
            point = geojson.Point(coords[i])
            neighbors.append(geojson.Feature(geometry=point))
    neighbors = geojson.FeatureCollection(neighbors)
    
    
    return neighbors #(str(nearNum),neighbors) #result_feature #handle_response(neighbors)

@app.route('/displayNN')
def displayNearestNeigh():
    """
    http://localhost:7878/displayNN
    """
    NNresult = NN
    return handle_response(NNresult)


# ██╗  ██╗███████╗██╗     ██████╗ ███████╗██████╗     ███████╗██╗   ██╗███╗   ██╗ ██████╗████████╗██╗ ██████╗ ███╗   ██╗              ██████╗  █████╗ ████████╗ █████╗ 
# ██║  ██║██╔════╝██║     ██╔══██╗██╔════╝██╔══██╗    ██╔════╝██║   ██║████╗  ██║██╔════╝╚══██╔══╝██║██╔═══██╗████╗  ██║              ██╔══██╗██╔══██╗╚══██╔══╝██╔══██╗
# ███████║█████╗  ██║     ██████╔╝█████╗  ██████╔╝    █████╗  ██║   ██║██╔██╗ ██║██║        ██║   ██║██║   ██║██╔██╗ ██║    █████╗    ██║  ██║███████║   ██║   ███████║
# ██╔══██║██╔══╝  ██║     ██╔═══╝ ██╔══╝  ██╔══██╗    ██╔══╝  ██║   ██║██║╚██╗██║██║        ██║   ██║██║   ██║██║╚██╗██║    ╚════╝    ██║  ██║██╔══██║   ██║   ██╔══██║
# ██║  ██║███████╗███████╗██║     ███████╗██║  ██║    ██║     ╚██████╔╝██║ ╚████║╚██████╗   ██║   ██║╚██████╔╝██║ ╚████║              ██████╔╝██║  ██║   ██║   ██║  ██║
# ╚═╝  ╚═╝╚══════╝╚══════╝╚═╝     ╚══════╝╚═╝  ╚═╝    ╚═╝      ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝   ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝              ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝

UFO = load_data("/home/ladelle/public_html/ProjectTest/assets/api/data/fixed_ufos.geojson")
STATES = load_data("5443-Spatial-DS-Augustine/Assignments/A04/assets/api/data/states.json")
STATES2 = load_data("5443-Spatial-DS-Augustine/Assignments/A04/assets/api/data/states.json")
EARTHQ = load_data("5443-Spatial-DS-Augustine/Assignments/A04/assets/api/data/earthquake_data/earthquakes/2020_1.json")
RROADS = load_data("TestingProgram/Railroads.geojson/Railroads.geojson")
STATES_BBOXS = load_data("5443-Spatial-DS-Augustine/Assignments/A04/assets/api/data/us_states_bbox.csv")
CITIES =load_data("5443-Spatial-DS-Augustine/Assignments/A04/assets/api/data/countries_states/major_cities.geojson")     
MILBASE = load_data('5443-Spatial-DS-Augustine/Assignments/A04/assets/api/data/military_bases.geojson')
NN = load_data('/Users/Delly/Desktop/NewEnv/5443-Spatial-DS-Augustine/Assignments/A04/assets/api/data/mapPoints.geojson')
# VOLC = load_data('/home/ladelle/public_html/ProjectTest/assets/api/data/volcano.json')
# ----------------------------- PROJECT ---------------------------------------------------------------------
MAJORROADS = ('/home/ladelle/public_html/TestingProgram/Primary_Roads.geojson/Primary_Roads_shapefiles.shp')
shapefileToGraph = nx.read_shp(MAJORROADS, simplify = False, geom_attrs = True, strict = True)
G2 = shapefileToGraph.to_undirected()
setNames = ['UFO','STATES' ,'EARTHQ','CITIES','MILBASE' ,'STATES_BBOXS', 'RROADS']
dataSets = [UFO,STATES, EARTHQ,CITIES, MILBASE,STATES_BBOXS,  RROADS]







# ██████╗ ██████╗ ██╗██╗   ██╗ █████╗ ████████╗███████╗    ███████╗██╗   ██╗███╗   ██╗ ██████╗████████╗██╗ ██████╗ ███╗   ██╗███████╗
# ██╔══██╗██╔══██╗██║██║   ██║██╔══██╗╚══██╔══╝██╔════╝    ██╔════╝██║   ██║████╗  ██║██╔════╝╚══██╔══╝██║██╔═══██╗████╗  ██║██╔════╝
# ██████╔╝██████╔╝██║██║   ██║███████║   ██║   █████╗      █████╗  ██║   ██║██╔██╗ ██║██║        ██║   ██║██║   ██║██╔██╗ ██║███████╗
# ██╔═══╝ ██╔══██╗██║╚██╗ ██╔╝██╔══██║   ██║   ██╔══╝      ██╔══╝  ██║   ██║██║╚██╗██║██║        ██║   ██║██║   ██║██║╚██╗██║╚════██║
# ██║     ██║  ██║██║ ╚████╔╝ ██║  ██║   ██║   ███████╗    ██║     ╚██████╔╝██║ ╚████║╚██████╗   ██║   ██║╚██████╔╝██║ ╚████║███████║
# ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═══╝  ╚═╝  ╚═╝   ╚═╝   ╚══════╝    ╚═╝      ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝   ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝
sid = -1
result_feature ={
    'type': 'FeatureCollection',
    'features':[],
}


  
  
# created bounding box----------------------
def point_to_bbox(lng, lat, offset=.001):
    return (float(lng-offset), float(lat-offset), float(lng+offset), float(lat+offset))



def convertTOGEOJSON(data, ftype):
    """
    converts coordinates to geojson 

    """ 
    ftype = ftype.lower()
    
    if ftype == "point":
        result_feat =[]
        for i in range(0,len(data)):
            point = geojson.Point(data[i])
            result_feat.append(geojson.Feature(geometry=point))
        result_feat = geojson.FeatureCollection(result_feat)
        # pp.pprint(collection) # valid
        return result_feat

    if ftype == "polygon":
        polygon = geojson.Polygon(data)
        # print(polygon)  # valid  
        return polygon

    elif ftype == "linestring":
        linestring = geojson.LineString(data)
        # print(linestring) #valid
        return (linestring)

    elif ftype == "multilinestring":
        mls = geojson.MultiLineString(data)
        # print(mls) # valid
        return mls

    else:
        print("\nwrong argument\n")
  

def handle_response(data,params=None,error=None):
    success = True
    if data:
        if not isinstance(data,list):
            data = data
        count = len(data)
    else:
        count = 0
        error = "Data variable is empty!"
    
    # result = {"success":success,"count":count, "FeatureCollection": data,"sid": params}
    result = data
    # if error:
    #     success = False
    #     result['error'] = error
    

    return jsonify(result)

#THIS IS FOR BOUNDING BOX 
def handle_response2(data,params=None,error=None):
    success = True
    if data:
        if not isinstance(data,list):
            data = data
        count = len(data)
    else:
        count = 0
        error = "Data variable is empty!"

    result = {"results":data,"success":success,"count":count }
   
    if error:
        success = False
        result['error'] = error
    

    return jsonify(result)

def toGeoJson(data, dtype):
    """formats all data input to valid geojson
    """
    dtype = dtype.lower()
    if dtype == "point":
        collection =[]
        for i in range(0,len(data)):
            point = geojson.Point(data[i])
            collection.append(geojson.Feature(geometry=point))
        collection = geojson.FeatureCollection(collection)
        # pp.pprint(collection) # valid
        return collection
    if dtype == "polygon":
        polygon = geojson.Polygon(data)
        # print(polygon)  # valid  
        return polygon
    elif dtype == "linestring":
        linestring = geojson.LineString(data)
        # print(linestring) #valid
        return (linestring)
    elif dtype == "multilinestring":
        mls = geojson.MultiLineString(data)
        # print(mls) # valid
        return mls
    else:
        print("\nBAD ARGUMENT\n")

def formatHelp(route):
    """Gets the __doc__ text from a method and formats it for easier reading
        This is __doc__ text
    """
    help = globals().get(str(route)).__doc__
    if help != None:
        help = help.split("\n")
        clean_help = []
        for i in range(len(help)):
            help[i] = help[i].rstrip()
            if len(help[i]) > 0:
                clean_help.append(help[i])
    else:
        clean_help = "No Help Provided."
    return clean_help


def isFloat(string):
    try:
        float(string)
        return True
    except ValueError:
        return False
 




if __name__ == '__main__':
    tree, coords = getTree()
    idx, rtreeID = getRTree()
    app.run(host='localhost', port=7878,debug=True)