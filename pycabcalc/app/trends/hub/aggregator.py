import pandas as pd
from datetime import datetime, timedelta
from ...db.taxiDB import TripQ
from ...geo import tools as geotools
import numpy as np 
import datetime
import time
import calendar
from sklearn.neighbors import NearestNeighbors
import os
import random
import pandas as pd

"""
Computes aggregated pickup/drop off trends for number of precomputed hubs.
Hubs are points in the city (expressed in long/lat coordinates) which serve as agggregation points.

This module computes the total count of pickup/dropoff events that happened in the vicinity of each hub
on a particular weekday (Mon, Tue...) of a particular month.

Results of the aggregation are saved in the local file for further processing and trend display.
"""

db_obj = TripQ()

def computeHubOccupancy(fname = "hub_occupancy.csv", typ = 'drop'):
    """
    Uses precomputed list of hub points and counts the number of pickup/dropoff points in the vicinity of each hub for different times of the day.
    Compute pickup/drop off trends for all months, accross all days of the week on hourly basis
    Save all results into a single file.
    """

    out_folder = os.path.dirname(os.path.abspath(__file__)) #dir of this module
    hubs_fname = out_folder+'/nyc_hubs.csv'
    res_fname = out_folder+"/"+fname

    f = open(res_fname, 'w')
    
    initial = True
    for month in range(10,11):
        for day in range(0,7):
            occ_month = _occupancy(month,day,hubs_fname, typ, 50000)

            if initial:
                occ_month.to_csv(f)    
                initial = False
            else:
                occ_month.to_csv(f, header = False)

            f.flush()

    f.close()

def _occupancy(month, day, hubs_fname, typ = 'drop', max_sampl_cnt = 50000):
    
    global db_obj

    df_hubs = pd.read_csv(hubs_fname, names=['lat', 'long']) #load hubs - i.e. points in which vicinity we search for the points
    df_hubs["tools, df_hubs["y"] = zip(*df_hubs[['long', 'lat']].apply(lambda row: geotools.sphericalConversion(*row.values), axis=1))
    
    #fetch pick up / drop off points
    if typ == 'pick':
        df = db_obj.query_Month(month, ["HOUR(pick_date) AS hour", "MINUTE(pick_date) AS minute", "pick_x AS x", "pick_y AS y"], dof_pick=day)

    elif typ == 'drop':
        #drop_date ommitted from the db to save space - compute it using pick_date and trip duration
        df = db_obj.query_Month(month, ["pick_date", "trip_time_in_secs AS dur", "drop_x AS x", "drop_y AS y"], dof_pick=day)
        df['drop_date'] = df['pick_date'].apply(lambda x: x.to_datetime()) + df['dur'].apply(lambda x:timedelta(seconds=x))
        df['hour'] = df['drop_date'].apply(lambda x: x.hour)
        df['minute'] = df['drop_date'].apply(lambda x: x.minute)

    #Subsample frame randomly
    if max_sampl_cnt and len(df)> max_sampl_cnt:
        rand_ri = random.sample(df.index, max_sampl_cnt) #todo count the exact no of days of type day in a given month
        df = df.ix[rand_ri]
        print len(df)

    #Build model
    nbrs = NearestNeighbors(n_neighbors=1, algorithm='ball_tree').fit(df_hubs[['x', 'y']].values)
    
    #For each picup /drop off point find the nearest hub and increase its counter by one - do this separately for each hour
    hour_gr = df.groupby('hour')
    df_hubs_tot = pd.DataFrame([]) #will contain all counts for each hour accross different hubs
    for hi in hour_gr:
        
        data = hi[1]
        df_hubs_hour = df_hubs.copy() #count for each hub in one hour
        df_hubs_hour["count"] = 0 #no of points close to this hub

        for ind, di in data.iterrows(): 
            m = nbrs.kneighbors(di[['x', 'y']].values)[1][0][0]
            df_hubs_hour['count'][m] += 1
        df_hubs_hour['hour'] = hi[0]
        df_hubs_tot = pd.concat([df_hubs_tot, df_hubs_hour])

    df_hubs_tot['month'] = month
    df_hubs_tot['day'] = day

    return df_hubs_tot
