import matplotlib.path as mplPath
from ..geo import basic as geoloc
import numpy as np

import db_util as db
import math

"""
Module for marking records that have both start/end points on the Manhattan island (i.e. excluding other NYC boroughs)
"""

def mark(month):

    tblSz = db.tblSz(month)
    chunkSz = 200000
    dbChunks = int(math.ceil(tblSz/(1.*chunkSz)))

    #Performing the operation on the chunk of data - to push the interim results to the db after they have finished
    for chunk in range(dbChunks):

        #start and end ord no of records retrieved
        si = chunk*chunkSz
        ei = (chunk+1)*chunkSz-1

        print "Chunk...", si, ei

        df = db.load(month, si, ei)

        _checkManhattanBox(df)
        _updateErrFlag(df)
        _deleteTempColumns(df)

        print "Storing...", si, ei
        db.push2Db(month, df, columns=['err_flag'])


def _checkManhattanBox(df):

    """
    Use Manhattan bounding box to eliminate all non Manhattan records (i.e. trips that begin/terminate outside Manhattan island)
    """
    Manhattan_BBox_latlon = [(40.692142,-74.029655), (40.756409,-74.014206), (40.831005,-73.960991), (40.880343,-73.935242), (40.872296,-73.907433),(40.834382,-73.933868),(40.808921,-73.933182), (40.801218,-73.925629),(40.775131,-73.940392),(40.733259,-73.970947),(40.708540,-73.972664),(40.704896,-73.995667)]
    Manhattan_BBox_xy = [geoloc.sphericalConversion(lon, lat) for lat, lon in Manhattan_BBox_latlon]
    bbox = mplPath.Path(np.array(Manhattan_BBox_xy))
    
    try:
        df['manhattan'] = df.apply(lambda row:bbox.contains_point((row['pick_x'], row['pick_y'])) + bbox.contains_point((row['drop_x'], row['drop_y'])) ==2 , axis = 1)
    
    except:
            print "Some error... Exiting!"
            pass #silently exit

def _deleteTempColumns(df):
    """
    Deletes extra columns inserted in this procedure.
    """
    del df['manhattan']

def _updateErrFlag(df):
    """ Sets err flag to 1 if one of the route points falls outside Manhattan island"""

    markFunc = lambda row: 1 if not row['manhattan'] else row['err_flag']
    df.err_flag = df.apply(markFunc, axis=1)


