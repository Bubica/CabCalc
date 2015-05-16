import matplotlib.path as mplPath
from ..geo import basic as geoloc
import numpy as np

import math
from ..db import taxiDB 

"""
Module for marking records that have both start/end points on the Manhattan island (i.e. excluding other NYC boroughs)
"""

def mark(month):

    chunk_sz = 20000
    trip_handler = taxiDB.TripQ()

    chunk_iter = trip_handler.query_Month_Piecewise(month, chunkSz=chunk_sz)

    cnt = 0
    #Performing the operation on the chunk of data - to push the interim results to the db after they have finished
    for df in chunk_iter:

        print "Next chunk, month: ", month, " Count:", cnt, 
        cnt +=1

        _checkManhattanBox(df)

        print "Storing..."
        trip_handler.push2Db(month, df, match_column = 'ord_no', store_columns=['manhattan'])


def _checkManhattanBox(df):

    """
    Use Manhattan bounding box to eliminate all non Manhattan records (i.e. trips that begin/terminate outside Manhattan island)
    """
    Manhattan_BBox_latlon = [(40.692142,-74.029655), (40.756409,-74.014206), (40.831005,-73.960991), (40.880343,-73.935242), (40.872296,-73.907433),(40.834382,-73.933868),(40.808921,-73.933182), (40.801218,-73.925629),(40.775131,-73.940392),(40.733259,-73.970947),(40.708540,-73.972664),(40.704896,-73.995667)]
    Manhattan_BBox_xy = [geoloc.sphericalConversion(lon, lat) for lat, lon in Manhattan_BBox_latlon]
    bbox = mplPath.Path(np.array(Manhattan_BBox_xy))
    
    try:
        df['manhattan'] = df.apply(lambda row: bbox.contains_point((row['pick_x'], row['pick_y'])) + bbox.contains_point((row['drop_x'], row['drop_y'])) ==2 , axis = 1)
        df['manhattan'] = df['manhattan'].map(lambda x: 1 if x else 0) #boolean to 0/1 int

    except:
            print "Some error... Exiting!"
            pass #silently exit




