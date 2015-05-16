import math
import numpy as np
from math import radians, cos, sin, asin, sqrt


def sphericalConversion(lon, lat):
    """ Converts lon/lat (in deg) into cartesian - rough estimation suitable for a small geo areas """
    R = 3959; #in miles #in km = 6371

    xCart = R * math.cos(np.deg2rad(lat)) * math.cos(np.deg2rad(lon));
    yCart = R * math.cos(np.deg2rad(lat)) * math.sin(np.deg2rad(lon));
    
    return xCart, yCart

def toLonLat(x,y):
   """ Reverse of sphericalConversion """

   R = 3959
   lat = np.rad2deg(math.asin(math.sqrt(R**2 - x**2 - y**2) / R))
   lon = np.rad2deg(math.atan2(y, x))

   return (lon, lat)


def calcDistance1(p1, p2):
    p1xy = sphericalConversion(*p1)
    p2xy = sphericalConversion(*p2)

    return math.sqrt((p1xy[0]-p2xy[0])**2 + (p1xy[1]-p2xy[1])**2)

def calcDistance(p1, p2): #points in lon lat

      lat1 = p1[1]
      lon1 = p1[0]
      lat2 = p2[1]
      lon2 = p2[0]
      
      #Code taken from: http://stackoverflow.com/questions/4913349/haversine-formula-in-python-bearing-and-distance-between-two-gps-points
      """
      Calculate the great circle distance between two points 
      on the earth (specified in decimal degrees)
      """
      # convert decimal degrees to radians 
      lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

      # haversine formula 
      dlon = lon2 - lon1 
      dlat = lat2 - lat1 
      a = sin(dlat/2.)**2 + cos(lat1) * cos(lat2) * sin(dlon/2.)**2
      c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a)); 

      # 6367 km is the radius of the Earth
      miles = 3959 * c
      return miles

