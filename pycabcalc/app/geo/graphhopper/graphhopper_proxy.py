import urllib2
import json
import sys
import time

"""
Proxy for composing routing requests to Graphhopper server running on http://localhost:8989.

Prior to executing methods from this module, start the server in the terminal with:

>>> cd /Users/bubica/Development/CODE/PROJECTS/InsightDataScience2014/Project/resources/graphhopper
>>> ./graphhopper.sh web north-america_us_new-york.pbf

"""

def getDistance(start_lonlat, end_lonlat):

    """
    Input: two lon/lat tuples.
    Output: length of the shortest returned path (driving) between given points.
    """

    routeReqUrl = "http://localhost:8989/route?"
    routeReqUrl += "point=" + str(start_lonlat[1]) + "%2C" + str(start_lonlat[0])
    routeReqUrl += "&"
    routeReqUrl += "point=" + str(end_lonlat[1]) + "%2C" + str(end_lonlat[0])

    try:
        res = json.load(urllib2.urlopen(routeReqUrl))
        paths = res['paths']

        dist = sys.maxint
        for p in paths:
            dist = min([p['distance'], dist])
        
        dist = 0.621371192 * dist/1000. #convert metres to miles
        return dist

    except KeyError:
        return -1

    except : #catch all errors
        print "Unexpected error:", sys.exc_info()[0]
        return -1


