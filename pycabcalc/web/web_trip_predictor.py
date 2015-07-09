import pandas as pd
import numpy as np
import datetime
import time
import calendar

from ..app.trip_predict.predictor.location_aware import TripPredictor
from ..app.trip_predict.predictor.location_aware import InsufficientDataError
from ..app.trip_predict.models import gradientBoost as model_grad
from ..app.geo import google_loc

"""
Module for running main predictor selected for the web app.
"""

def _prep_locations(str_start_p, str_end_p):
    
    #Get coordinates of the given start/end points
    if " NYC" not in str_start_p:
        str_start_p = str_start_p+", NYC, USA"
    if " NYC" not in str_end_p:
        str_end_p = str_end_p+", NYC, USA"
        
    print 
    print "PREFORMATTED", str_start_p
    print "PREFORMATTED", str_end_p
    print 

    start_p, start_add_formatted = google_loc.getCoordFromAddress(str_start_p, True)
    end_p, end_add_formatted = google_loc.getCoordFromAddress(str_end_p, True)

    #"New York, NY, USA" is the default coordinate when address is not found
    # Use this as an indicator that the provided address is not correct one

    if start_p == None or start_add_formatted == "New York, NY, USA": 
        start_add_formatted = None

    elif end_p==None or end_add_formatted == "New York, NY, USA":
        end_add_formatted = None
    
    else:
        #formatted addresses (displayed in the output)
        start_add_formatted = start_add_formatted.split(',')[0]
        end_add_formatted = end_add_formatted.split(',')[0]

    print 
    print "FORMATTED", start_add_formatted
    print "FORMATTED", end_add_formatted
    print 

    return start_p, start_add_formatted, end_p, end_add_formatted

def _prep_date (t, date):
    
    """ Check the input time data and convert the format """

    try:
        t_datetime = datetime.datetime.strptime(date+" "+t, "%Y-%m-%d %H:%M")
    except ValueError:
        return None

    return t_datetime

def get_est(str_start_p, str_end_p, t, date, walk_est = True):


    #Prepare the format of pickup/dropoff location points
    start_p, start_add_formatted, end_p, end_add_formatted = _prep_locations(str_start_p, str_end_p)

    if not start_add_formatted:
        return ("","","","","","Origin not recognized")

    if not end_add_formatted:
        return ("","","","","","Destination not recognized")


    #Prepare format of time of pickup
    t_datetime = _prep_date(t, date)

    if not t_datetime:
        return ("","","","","","Malformed time/date. Required format: YYYY-MM-DD, HH:MM")

    if 'airport' in start_add_formatted.lower() or 'airport' in end_add_formatted.lower():
        search_area = 1.
    else:
        search_area = 0.3

    done_flag = False
    while search_area < 5 and not done_flag:
        try:
            #Create predictor obj - todo place the setup in config file
            predict_obj = TripPredictor(interval_sz=60, limit = 5000, model = model_grad, search_area=search_area, modelParams={"n_estimators": 50, "learn_rate":0.1, "max_depth":3})

            #Get estimates
            durEst_norain, fareEst_norain, durEst_rain, fareEst_rain, _ = predict_obj.getEstimates(start_p, end_p, t_datetime)

            done_flag = True

        except InsufficientDataError:
            #No enough data available to build a model - increase the search area (by 2.5 factor) and repeat
            print 
            print "Increasing the search size to ", search_area * 2.5
            print
            search_area *= 2.5
            

    if not done_flag:
        return ("","","","","","Sorry, not enough data to predict this route :(.")

    #get duration estimate of walk (for comparison)
    walk_dur = None
    if walk_est:        
        try:
            walk_dur = google_loc.getDistance(start_p, end_p, travel_mode="walking")[1]/60. #im mins
            walk_dur = round(walk_dur,2)
        except:
            #if the distance is too long to walk, google will return no results...
            pass 

    print 
    print "RESULT", durEst_norain, fareEst_norain, durEst_rain, fareEst_rain
    print
    
    return durEst_norain, fareEst_norain, durEst_rain, fareEst_rain, walk_dur, start_add_formatted, end_add_formatted, None
    