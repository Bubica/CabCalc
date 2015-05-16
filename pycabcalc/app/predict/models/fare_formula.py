import sys
sys.path.append('/Users/bubica/Development/CODE/InsightDataScience2014/Project/code/python/map_handler')
#from ..map_handler import gmaps
import googmp as gm
import numpy as np
import datetime


#Validation
import err_score as err

def run(df_test):
    
    #evaluation of fare using formula
    df_test['speed'] = df_test.apply(lambda row: row['trip_distance']/(1.*row['trip_time_in_secs']) * 3600., axis = 1) #mph

    y_predicted = df_test.apply(lambda row: estimate(row['trip_distance'], row['trip_time_in_secs'], row['pick_date'], row['speed']), axis = 1).values
    y_test = df_test['total_wo_tip'].values

    # avr_speed_train = 
    # for xi in df_test:
    #     s_lon = xi[0]
    #     s_lat = xi[1]
    #     e_lon = xi[2]
    #     e_lat = xi[3]
    #     t = xi[4]

    #     # f = _estimateGoogle((s_lon, s_lat), (e_lon, e_lat), t)
    #     y_predicted.append(f)

    #Validation
    rmse = err.RMSE(y_predicted, y_test)
    r2 = err.Rsquare(y_predicted, y_test)

    return y_predicted, rmse, r2


# #Estimates fare based on the distance and travel time
# def _estimateGoogle(startLongLat, endLongLat, t): #t must be a datetime object
    
#     #From: http://www.nyc.gov/html/tlc/html/passenger/taxicab_rate.shtml
#     e_distance_met,  driving_time_s = gm.googleDistMatrixEst(startLongLat, endLongLat)
#     dist_mile = e_distance_met*0.000621371192
    
#     speed_ms = dist_mile / (1.* driving_time_s)#ms
#     speed_mph = speed_ms / 0.44704 #mph units
    
#     return _estimate(dist_mile, driving_time_s, t, speed_mph)

def estimate(dist_mile, driving_time_s, date, speed_mph=13):
    
    #Generic fare estimate formula

    unit_p = 0.50
    start_fee = 2.5
    night_sur = 0.5
    peak_sur = 0.5
    tax = 0.5

    total_p = start_fee #start fee

    if speed_mph >= 12:
        total_p = total_p + dist_mile*5. * unit_p
    else:
        total_p = total_p +  driving_time_s/60. * unit_p
    
    day = date.day
    weekday = date.weekday()
    h = date.hour #24 h format
    
    if h>=20 or h<6:
        total_p = total_p + night_sur
    
    if (weekday >= 0 and weekday <= 5) and (h>=16 and h<20):
        total_p = total_p + peak_sur
        
    total_p = total_p + tax
    
    return total_p