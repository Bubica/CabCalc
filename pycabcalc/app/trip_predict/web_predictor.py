import geo.google_loc as gmh 
import pandas as pd
from geo import basic as geoloc
import numpy as np

import datetime
import time
import calendar
import os

from predict.predict import TripPredictor

"""
Module for running main predictor selected for the web.
"""

# def _dur_est(df, dist, date):
#     #Keep only times in the dataframe that are around the requested one
#     h_req = date.hour
    
#     h1 = (h_req-1+24)%24
#     h2 = (h_req+1)%24

#     if h1< h2:
#         df = df[(df['hour']>h1) & (df['hour']<h2)]
#     else:
#         df = df[(df['hour']>h1) | (df['hour']<h2)]

#     X_train = df['trip_distance'].values
#     y_train = df['trip_time_in_secs'].values

#     X_test = [dist]
#     y_test = [10] #some arbitrary value

#     y_pred, _,_ = model_bag.run(X_train, X_test, y_train, y_test) 
#     est = round(y_pred[0]/60., 2)

#     return est

def _dur_est(df, dist, date):
    X_train = df[['trip_distance', 'weekday', 'hour']].values
    y_train = df['trip_time_in_secs'].values

    X_test = np.array([[dist, date.weekday(), date.hour]])
    y_test = [10]

    y_pred, _,_,_ = model_grad.run(X_train, X_test, y_train, y_test) 
    est = round(y_pred[0]/60., 2) #convert to minutes

    return est

def _fare_est(df, dist, date):
          
    X_train = df[['trip_distance', 'weekday', 'hour']].values
    y_train = df['total_wo_tip'].values

    X_test = np.array([[dist, date.weekday(), date.hour]])
    y_test = [10]

    y_pred, _,_, _ = model_grad.run(X_train, X_test, y_train, y_test) 
    est = round(y_pred[0], 2)

    return est

def get_est(str_start_p, str_end_p, t, date):

    # _init()

    #Quick check of locations, without NY addon
    # start_p = gmh.getCoordFromAddress(str_start_p)
    # end_p = gmh.getCoordFromAddress(str_end_p)

    # print "++++++++++++ check"
    # print start_p
    # print end_p
    # if start_p == None:
    #     return ("","","","Source not recognized")

    # if end_p==None:
    #     return ("","","","Destination not recognized")

    #Get coordinates of the given start/end points
    if " NYC" not in str_start_p:
        str_start_p = str_start_p+", NYC"
    if " NYC" not in str_end_p:
        str_end_p = str_end_p+", NYC"
        
    start_p, start_add_formatted = gmh.getCoordFromAddress(str_start_p, True)
    end_p, end_add_formatted = gmh.getCoordFromAddress(str_end_p, True)

    #"New York, NY, USA" is the default coordinate when address is not found
    # Use this as an indicator that the provided address is not correct one

    print
    print "++++++++++++ check"
    print start_p, start_add_formatted
    print end_p, end_add_formatted
    print

    if start_p == None or start_add_formatted == "New York, NY, USA": 
        return ("","","","","","Origin not recognized")

    if end_p==None or end_add_formatted == "New York, NY, USA":
        return ("","","","","","Destination not recognized")

    dist = gmh.googleDistMatrixEst(str_start_p, str_end_p)[0]

    mile_dia = 0.3

    start_p = geoloc.sphericalConversion(*start_p)
    end_p = geoloc.sphericalConversion(*end_p)

    #formatted addresses (displayed in the output)
    start_add_formatted = start_add_formatted.split(',')[0]
    end_add_formatted = end_add_formatted.split(',')[0]

    #Define two time intervals train (t1-t2) test(t2-t3)
    try:
        t_req = datetime.datetime.strptime(date+" "+t, "%Y-%m-%d %H:%M")
    except ValueError:
        return ("","","","","","Malformed time/date. Required format: YYYY-MM-DD, HH:MM")

    h_req = t_req.hour
    month_req = t_req.month
    year_req = t_req.year

    if year_req<2014 or year_req>2016:
        return ("","","","","","Malformed year.")

    month_max_day = calendar.monthrange(2013,month_req)[1]

    t_2013_end =  datetime.datetime(2013, t_req.month, t_req.day, t_req.hour, t_req.minute, t_req.second)
    t_2013_end = t_2013_end - datetime.timedelta(days=1) #do not include the requested day
    t_2013_start = t_2013_end -  datetime.timedelta(days=60)
    

    #Extract routes
    t_perf1 = time.time()
    lim=8000
    df_train = db_trip.query_Routes(start_p, end_p, mile_dia, lonLat=False, date_span = (t_2013_start, t_2013_end), limit=lim, fareJoin = True)
    t_perf2 = time.time()

    print "Query time: ", t_perf2 - t_perf1 , "s"
    print 'Retrieved: ', len(df_train)

    if len(df_train)<=0:
        return ("", "", "", "", "","No sufficent number of routes found.")

    #Add features
    df_train['weekday'] = df_train.apply(lambda row: row['pick_date'].weekday(), axis=1) 
    df_train['hour'] = df_train.apply(lambda row: row['pick_date'].hour, axis=1)

    #Run the estimators
    dur_est = _dur_est (df_train, dist, t_req) #in secs
    fare_est = _fare_est(df_train, dist, t_req) 

    #estimate walk duration as well
    walk_dur = gmh.googleDistMatrixEst(str_start_p, str_end_p, travel_mode="walking")[1]/60. #im mins
    walk_dur = round(walk_dur,2)

    return (dur_est, fare_est, walk_dur, start_add_formatted, end_add_formatted, None)




def _debug():

    #Debugging & testing
    ts = time.time()

    str_start_p = "Union Square, NYC, USA"
    str_end_p = "Times Square, NYC, USA"

    #Obtain loaction data from Google services (lon/lat coordinates and approx. route distance)
    done_flg = False
    while not done_flg:
        try:
            dist = gmh.googleDistMatrixEst(str_start_p, str_end_p)[0]
            start_p, start_add_formatted = gmh.getCoordFromAddress(str_start_p, True)
            end_p, end_add_formatted = gmh.getCoordFromAddress(str_end_p, True)

            done_flg = True
        except IOError:
            print "IOError occurred. Trying again..."

    date = datetime.datetime(2015, 4, 16, 17, 44, 0)

    import predict.predict as predict
    predictObj = predict.TripPredictor()
    estDur, estFare = predictObj.getEstimates(start_p, end_p, dist, date)

    te = time.time()
    
    print "Total running time is %f seconds" % (te-ts)
    return estDur, estFare

