#Getting the estimate of travel duation and distance from Google Distance matrix
import simplejson, urllib
from google.directions import GoogleDirections
import pandas as pd
import urllib, cStringIO
import re
import os
import sys
import time
import ConfigParser

"""
Module provides interface to google location services.
"""
config = ConfigParser.ConfigParser()
config.read(os.path.dirname(__file__)+"/"+"key.ini")
googleApiKey = config.get('Google', 'key')


def getDistance(orig, dest, travel_mode="driving"):
    """
    Given the starting and ending location provided in coordinates or string format, 
    return the distance (in miles) and travel time between these two points
    travel_mode: walking or driving
    """

    if (type(orig) == str and type(dest) ==str) or (type(orig) == unicode and type(dest) == unicode):
        return _distFromText (orig, dest, travel_mode)

    elif type(orig) == tuple and type(dest) ==tuple:
        return _distFromCoord (orig, dest, travel_mode)

    else:
        print type(orig), type(dest)
        raise ValueError ("Malformed input!")

def _distFromCoord(orig_coord = (-73.990602, 40.731779), dest_coord =  (-73.976709, 40.731779), travel_mode="driving"):

    print "Fetching distance info using Google service... (coord input) "

    o = str(orig_coord[1])+","+str(orig_coord[0])
    d = str(dest_coord[1])+","+str(dest_coord[0])
    url = ("http://maps.googleapis.com/maps/api/distancematrix/json?origins={0}&destinations={1}&mode="+travel_mode+"&language=en-EN&sensor=false").format(o,d)
    
    print
    print url
    print

    result= simplejson.load(urllib.urlopen(url))

    travel_time = result['rows'][0]['elements'][0]['duration']['value']# in seconds
    distance = result['rows'][0]['elements'][0]['distance']['value'] #in metres
    dist_miles = distance * 0.00062

    time.sleep(0.4) #to limit the number of requests per sec (max 10)

    return dist_miles, travel_time

def _distFromText(orig_str, dest_str, travel_mode):

    print "Fetching distance between %s and %s " %(orig_str, dest_str)

    url = ("http://maps.googleapis.com/maps/api/distancematrix/json?origins={0}&destinations={1}&mode="+travel_mode+"&language=en-EN&sensor=false").format(orig_str,dest_str)
    
    print
    print url
    print

    result= simplejson.load(urllib.urlopen(url))

    travel_time = result['rows'][0]['elements'][0]['duration']['value']# in seconds
    distance = result['rows'][0]['elements'][0]['distance']['value'] #in metres
    dist_miles = distance * 0.00062
    return dist_miles, travel_time

def getStaticImage(center_lat = 40.7338871, center_lng=-73.9911071, zoom=13, fileName = None): 
    """
    Fetches a static google map Image
    """
    url = "http://maps.googleapis.com/maps/api/staticmap?center={0},{1}&zoom={2}&size=2048x2048".format(center_lat, center_lng, zoom)
    fr = urllib.urlopen(url).read()
    f = cStringIO.StringIO(fr)
    
    if fileName is not None:
         fufa = open(fileName, 'w')
         fufa.write(fr)
         fufa.close()

    return f

def onManhattan(point_lat = 40.732779, point_lng=-73.976709):
     url="https://maps.googleapis.com/maps/api/geocode/json?address={0},{1}&key={2}".format(point_lat, point_lng, googleApiKey)
     result= simplejson.load(urllib.urlopen(url))

     try:
        address = result['results'][0]["formatted_address"]
     except IndexError:
        print "Err on: ", result
        return False

     if 'New York' not in address: return False

     plist = [s for s in address.split('New York')[1] if s.isdigit()]
     postcode = int(''.join(plist))

     return postcode < 10300
     
    

def getRoute(orig_coord = (-73.990602, 40.731779), dest_coord =  (-73.976709, 40.751687)):

    global googleApiKey

    st_code = 0

    sys.stdout.flush()

    while st_code is not 200:
        #Returns the list of routes Distance in metres and duration in sec (driving?!)
        gd = GoogleDirections(googleApiKey)
        try:
            res = gd.query(str((orig_coord[1], orig_coord[0])), str((dest_coord[1], dest_coord[0])))
        except TypeError:
            return None
        st_code = res.result['Status']['code']

    sys.stdout.flush()
    routes = res.result['Directions']["Routes"][0]['Steps']

    df = pd.DataFrame(routes, columns=['Distance', 'Duration', 'Point', 'polylineIndex'])

    df['Distance'] = df['Distance'].apply(lambda x: x['meters'])
    df['Duration'] = df['Duration'].apply(lambda x: x['seconds'])
    df['Point'] = df['Point'].apply(lambda x: x['coordinates'][:2])

    return df


def getTotDist(orig_coord = (-73.990602, 40.731779), dest_coord =  (-73.976709, 40.751687)):
    """
    Total distance between two points accross all route fractions
    """
    df_route = getRoute(orig_coord, dest_coord)
    if df_route is None: 
        return -1
    else:
        return df_route['Distance'].sum()

def getTotDur(orig_coord = (-73.990602, 40.731779), dest_coord =  (-73.976709, 40.751687)):
    """
    Total driving duration between two points accross all route fractions
    """
    df_route = getRoute(orig_coord, dest_coord)
    if df_route is None: 
        return -1
    else:
        return df_route['Duration'].sum()

def getCoordFromAddress(addrString, formattedAddress = False):
    #For given string addresses returns the lon/lat values

    url = ("https://maps.google.com/maps/api/geocode/json?address={0}&sensor=false&key={1}").format(addrString, googleApiKey)
    print "GOOGLE addr resolution: ", url

    result= simplejson.load(urllib.urlopen(url))

    if 'results' not in result or len(result['results'])<=0:
        if "error_message" in result:
            print
            print "ERROR:", result["error_message"]
            print
        return None
        
    lat = result['results'][0]['geometry']["location"]['lat']
    lng = result['results'][0]['geometry']["location"]['lng']
    form_add = result['results'][0]["formatted_address"]

    if formattedAddress:
        return (lng, lat), form_add
    else:
        return (lng, lat)



#transformation of google zoom levels to meter scale taken from http://gis.stackexchange.com/questions/7430/google-maps-zoom-level-ratio
zoom2metre_dict = {
20 : 1128.497220,
19 : 2256.994440,
18 : 4513.988880,
17 : 9027.977761,
16 : 18055.95552,
15 : 36111.91104,
14 : 72223.82209,
13 : 144447.6442,
12 : 288895.2884,
11 : 577790.5767,
10 : 1155581.153,
9  : 2311162.307,
8  : 4622324.614,
7  : 9244649.227,
6  : 18489298.45,
5  : 36978596.91,
4  : 73957193.82,
3  : 147914387.6,
2  : 295828775.3,
1  : 591657550.5} 
metre2zoom_dict = {zoom2metre_dict[k]:k for k in zoom2metre_dict.keys()} #for inverse lookups

#http://www.icesi.edu.co/CRAN/web/packages/RgoogleMaps/vignettes/RgoogleMaps-intro.pdf

def staticmap_pixels(lon, lat, zoom):
    lat_r = lat/180.*math.pi
    l = (1+math.sin(lat_r)) / (1-math.sin(lat_r))
    y_tld = 1/(2*math.pi) * math.log(l)
    x_tld = (lon/180)
    Y = 2**(zoom-1) * (1-y_tld)
    X = 2**(zoom-1) * (x_tld+1)

    return X,Y