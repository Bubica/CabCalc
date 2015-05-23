"""
Module for time profiling database select requests and building the model.

Results stored in: info/profiler_results/
"""

from .. import config
from ...trip_predict.predictor.location_aware import TripPredictor
from ...geo import google_loc

import os
import time
import subprocess

def _reset_cache():

    """ Reset query cache (between experiments) """

    print "Clean cache"

    bashCmd = 'mysql -e "RESET QUERY CACHE" -u root'
    ret_code = subprocess.call(bashCmd, shell=True)

    assert ret_code==0

def db_select_only(log_fname):
    
    """ 
    Only profiles the retrieval of data from the database (i.e. execution of select command)
    """
    sep = '|' #csv separator

    config_fname = os.path.dirname(__file__)+"/"+"default.ini"
    config.set_config_file(config_fname)

    routes = config.load_routes()
    routes_coord = {r: (google_loc.getCoordFromAddress(r[0], True)[0], google_loc.getCoordFromAddress(r[1], True)[0]) for r in routes}
       
    dates = config.load_dates()
    areas, max_samples, t_intervals = config.load_train_setup()

    log_f = open(log_fname, "a")
    log_f.write("Route_start"+sep+"Route_end"+sep+"Reference_time"+sep+"Interval(days)"+sep+"Area_size"+sep+"Max_samples"+sep+"Duration(s)"+sep+"Number_of_records\n") #header

    tp = TripPredictor()
    

    print 
    print "Config file:", config_fname, areas

    for day_cnt in t_intervals:
        for a in areas:
            for samp in max_samples:
                for r in routes:
                    
                    r0_lonlat = routes_coord[r][0] #google_loc.getCoordFromAddress(r[0], True)[0]
                    r1_lonlat = routes_coord[r][1] #google_loc.getCoordFromAddress(r[1], True)[0]
                    
                    for t in dates:
                        
                        print str(r[0])+sep+str(r[1])+sep+str(t)+sep+str(day_cnt)+sep+str(a)+sep+str(samp)+sep

                        tp = TripPredictor(search_area=a, interval_sz=day_cnt, limit=samp)
                        
                        #profile load time
                        ts = time.time()

                        tp._loadTrainData(t, r0_lonlat, r1_lonlat)
                        te = time.time()              
                        
                        _reset_cache()

                        t_delta = te-ts #in seconds
                        rec_count = len(tp.train_df) #total number of records retrieved

                        log_f.write(str(r[0])+sep+str(r[1])+sep+str(t)+sep+str(day_cnt)+sep+str(a)+sep+str(samp)+sep+str(t_delta)+sep+str(rec_count)+"\n")
                        log_f.flush()
