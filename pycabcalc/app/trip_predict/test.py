"""
Module for testing and debugging.
"""

import datetime

from ..geo import google_loc
from predictor import location_aware
from predictor import all_routes

def test_and_debug(module = all_routes):

    #Debugging & testing
    str_start_p = "Union Square, NYC, USA"
    str_end_p = "Times Square, NYC, USA"

    #Obtain loaction data from Google services (lon/lat coordinates and approx. route distance)
    done_flg = False
    while not done_flg:
        try:
            start_p, start_add_formatted = google_loc.getCoordFromAddress(str_start_p, True)
            end_p, end_add_formatted = google_loc.getCoordFromAddress(str_end_p, True)

            done_flg = True
        except IOError:
            print "IOError occurred. Trying again..."

    date = datetime.datetime(2015, 1, 16, 17, 44, 0)

    
    predictObj = module.TripPredictor(limit = 300)
    estDur, estFare, td = predictObj.getEstimates(start_p, end_p, date)
    
    print "Duration in sec: ", td
    
    return estDur, estFare