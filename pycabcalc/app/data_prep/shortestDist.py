"""
For every record in the database, computes the shortest distance between two poitns using the local Graphhopper
server. Result of each computation is stored in a new column in the database table.
"""

from ..geo.graphhopper import graphhopper_proxy as hop
from ..db import taxiDB 
from ..geo.tools import toLonLat

import math
import numpy as np
import pandas as pd


def mark(month):

    chunk_sz = 200000
    trip_handler = taxiDB.TripQ()

    chunk_iter = trip_handler.query_Month_Piecewise(month, chunkSz=chunk_sz)

    cnt = 0
    #Performing the operation on the chunk of data - to push the interim results to the db after they have finished
    for df in chunk_iter:

        print "Next chunk, month: ", month, " Count:", cnt, 
        cnt +=1

        df = _prepData(df)
        _computeShortestDist(df)
        _computeDeltas(df)
        _updateErrFlag(df)
        _deleteTempColumns(df)

        print "Storing..."
        trip_handler.push2Db(month, df, match_column = 'ord_no', store_columns=['err_flag'])



def _prepData(df):
    
    if 'pick_lon' not in df.columns or 'pick_lat' not in df.columns:
        f = lambda x: pd.Series(dict(zip(['pick_lon', 'pick_lat'], toLonLat(x['pick_x'], x['pick_y']))))
        lonLat_df = df.apply(f, axis=1)
        df = pd.concat([df, lonLat_df], axis=1)

    if 'drop_lon' not in df.columns or 'drop_lat' not in df.columns:
        f = lambda x: pd.Series(dict(zip(['drop_lon', 'drop_lat'], toLonLat(x['drop_x'], x['drop_y']))))
        lonLat_df = df.apply(f, axis=1)
        df = pd.concat([df, lonLat_df], axis=1)

    return df

def _computeShortestDist(df):

    """ Obtains the shortest route. Stores the interim result in the local structure"""

    spath = lambda record: hop.getDistance((record['pick_lon'], record['pick_lat']), (record['drop_lon'], record['drop_lat']))
    
    #Compute the shortest path for each taxi record 
    #Do this in chuncks (server tends to crash so make sure interim results are stored)
    df ['shortest_route'] = -1 # init the new column

    chunkSz = len(df)/1000
    chunkCnt = int(math.ceil(len(df)/(1.* chunkSz)))
    
    for c in range(1, chunkCnt):
        print "Chunk", c, "out of", chunkCnt
        df.ix[c * chunkSz : (c+1) * chunkSz, 'shortest_route'] = df[c * chunkSz : (c+1) * chunkSz].apply(spath, axis = 1)

def _computeDeltas(df):

    #Compute the delta between reported distance and shortest route
    shortDeltaFunc = lambda row: (row['shortest_route']) / row['trip_distance'] if row['shortest_route']>0 else np.nan
    df['short_delta'] =  df.apply(shortDeltaFunc, axis = 1)

    #Compute the euclidian distance
    euclFunc = lambda row: math.sqrt((row['drop_x']-row['pick_x'])**2 + (row['drop_y']-row['pick_y'])**2)
    df ['eucl_dist'] = df.apply(euclFunc, axis = 1)

    shortDeltaFunc = lambda row: (row['eucl_dist']) / row['trip_distance']
    df['eucl_delta'] = df.apply(shortDeltaFunc, axis = 1)


def _updateErrFlag(df):

    """ Updates ERR flag. Removes on average 5 percent of data"""

    #1. Omit distances shorter than Euclidian
    setErr = lambda row: 1 if row['eucl_delta']<0 else row['err_flag']
    df['err_flag'] = df.apply(setErr, axis=1)

    #2. Set flag if shortest dist is not calculated)
    setErr = lambda row: 1 if row['shortest_route']<0 else row['err_flag']
    df['err_flag'] = df.apply(setErr, axis=1)

    #3. Set flag if relative difference between shortest route and reported is >0.5 (absolute)
    setErr = lambda row: 1 if row['short_delta']<-0.5 or row['short_delta']>0.5 else row['err_flag']
    df['err_flag'] = df.apply(setErr, axis=1)

def _deleteTempColumns(df):

    """
    Deletes extra columns inserted in this procedure (shortest path is kept.
    """

    del df['short_delta']
    del df['eucl_dist']
    del df['eucl_delta']


def plot(df):

    #Plot histogram - Debugging purpose only
    df.hist(column=['short_delta'], bins = 500)
    pp.xlim(-2, 2)
    pp.xlabel("Relative difference between reported route length and the shortest one(from graphhopper)")

    df.hist(column=['eucl_delta'], bins = 500)
    pp.xlim(-2, 2)
    pp.xlabel("Relative difference between reported route length and the Euclidian")



        


