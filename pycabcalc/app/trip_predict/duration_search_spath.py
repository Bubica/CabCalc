
import sys
sys.path.append("/Users/bubica/insight_link/code/python")

from validation.setup import *
from grid_search import *
import itertools
import os
import pandas as pd
import db_handlers.local_mysql as db
import db_tripQueries as db_trip
import db_tripInserts as dbi
import trip_manip as tmanip
import geoloc
import numpy as np
import time
import datetime
import map_handler.googmp as gmh 
from map_handler import osm
from matplotlib import pyplot as pp
import sys
import log
import time

import models.baggingRegress as model_bag
import models.linearRegress as model_lin
import models.feasibleWLS as model_fwls
import models.randomForest as model_forest
import models.gradientBoost as model_grad


folder = "/Users/bubica/insight_link/code/python/validation/data/"

def search(all_routes=False):
    if all_routes:
        _train_set_all_routes()
    else:
        _train_set_routes()

def _train_set_all_routes():
    #Train set is a random collection of routes from the whole dataset, test set contains subset of spatially collocated routes

    init()
    global params
    testset = list(itertools.product(params['routes'], params['cluster_sz_test'])) #test setup

    finished = open(folder +"fin.txt", 'a')
    #Init data used for comparison

    logger = log.Logger()
    logger.set_file(folder+'res_dist_allroutes.csv')

    #Load train
    df_train = pd.read_csv(folder+"train_data_all_routes/train_1000000.csv",nrows = (params['max_train_sz']+10))[:params['max_test_sz']]
    df_train['pick_date'] = df_train.apply(lambda row: datetime.datetime.strptime(row['pick_date'], "%Y-%m-%d %H:%M:%S"), axis=1)
    df_train['drop_date'] = df_train.apply(lambda row: datetime.datetime.strptime(row['drop_date'], "%Y-%m-%d %H:%M:%S"), axis=1)
    df_train['weekday'] = df_train.apply(lambda row: row['pick_date'].weekday(), axis=1)
    df_train['hour'] = df_train.apply(lambda row: row['pick_date'].hour, axis=1)

    for tte, te in enumerate(testset):
        logger.log_comment("################## TEST: "+str(te)+" ##################")   
        if _isfinished(te): continue #test performed in full

        df_test = pd.read_csv(folder+"/test_data/test_df_"+str(tte)+".csv", nrows = (1000+10))[:1000]
        df_test['drop_date'] = df_test.apply(lambda row: datetime.datetime.strptime(row['drop_date'], "%Y-%m-%d %H:%M:%S"), axis=1)
        df_test['pick_date'] = df_test.apply(lambda row: datetime.datetime.strptime(row['pick_date'], "%Y-%m-%d %H:%M:%S"), axis=1)
        df_test['weekday'] = df_test.apply(lambda row: row['pick_date'].weekday(), axis=1) 
        df_test['hour'] = df_test.apply(lambda row: row['pick_date'].hour, axis=1)

        print "Loaded test"

        #Prepare basic log string
        id_test = str(tte)
        id_train= ""
        id_train_str = 'all'
        id_start = str(te[0][0])
        id_end = str(te[0][1])
        id_cl_test = str(te[1])
        id_cl_train = ""
        id_sz_test = str(len(df_test))
        id_sz_train = str(len(df_train))

        logger.log_id_test(str(tte))
        logger.log_id_train("")
        logger.log_id_train_str('all')
        logger.log_id_start(str(te[0][0]))
        logger.log_id_end(str(te[0][1]))
        logger.log_clust_test(str(te[1]))
        logger.log_clust_train('')
        logger.log_id_test(str(tte))
        logger.log_id_train("")
        logger.log_sz_test(str(len(df_test)))
        logger.log_sz_train(str(len(df_train)))

        runLinModels(df_train, df_test, _prepData_LinModels, params)
        runClassifRegressModels(df_train, df_test, _prepData_ClassifRegressModels, params)

        logger.reset_all()
        finished.write(str(te)+"\n")
        finished.flush()

        print "Done"

def _isfinished(te, tr=None):
    #temp file for logging what has been processed
    line = str(te)
    if tr is not None:
        line = line+","+str(tr)
    
    ff = open(folder +"fin.txt", 'r')
    s = ff.read()
    ff.close()

    if s.find(line)>-1:
        print "Found", s.find(line)
        return True
    else: 
        return False

def _train_set_routes():
    
    #Requires route matching in test and train files
    init()
    global params

    """
    testset = list(itertools.product(params['routes'], params['cluster_sz_test'])) #test setup
    trainset = list(itertools.product(params['routes'], params['cluster_sz_train'])) #train setup
    finished = open(folder +"fin.txt", 'a')

    logger = log.Logger()
    logger.set_file(folder+'res_dist_spath.csv')

    for tte, te in enumerate(testset)[:1]:
        logger.log_comment("################## TEST: "+str(te)+" ##################")   

        for ttr, tr in enumerate(trainset)[:2]:
            
            if not (te[0] == tr [0]): 
                continue #routes must match, cluster of test must be smaller or equal to the train?

            if _isfinished(te, tr): continue #test performed in full

            df_test = pd.read_csv(folder+"test_data/test_df_"+str(tte)+".csv", nrows = (1000+10))[:1000]
            df_test['drop_date'] = df_test.apply(lambda row: datetime.datetime.strptime(row['drop_date'], "%Y-%m-%d %H:%M:%S"), axis=1)
            df_test['pick_date'] = df_test.apply(lambda row: datetime.datetime.strptime(row['pick_date'], "%Y-%m-%d %H:%M:%S"), axis=1)
            df_test['weekday'] = df_test.apply(lambda row: row['pick_date'].weekday(), axis=1) 
            df_test['hour'] = df_test.apply(lambda row: row['pick_date'].hour, axis=1)
            calculate_shortest_path(df_test)

            print "Loaded test:", tte, te, "test_df_"+str(tte)+".csv", len(df_test)

            logger.log_comment("################## TRAIN"+str(tr)+" ##################")

            #Load train
            df_train = pd.read_csv(folder+"train_data_local_routes/train_df_"+str(ttr)+".csv", nrows = (params['max_train_sz']+10))[:params['max_train_sz']] #max million rows
            df_train['pick_date'] = df_train.apply(lambda row: datetime.datetime.strptime(row['pick_date'], "%Y-%m-%d %H:%M:%S"), axis=1)
            df_train['drop_date'] = df_train.apply(lambda row: datetime.datetime.strptime(row['drop_date'], "%Y-%m-%d %H:%M:%S"), axis=1)
            df_train['weekday'] = df_train.apply(lambda row: row['pick_date'].weekday(), axis=1)
            df_train['hour'] = df_train.apply(lambda row: row['pick_date'].hour, axis=1)

            if len(df_train) < 4*len(df_test): continue
           
            logger.log_id_test(str(tte))
            logger.log_id_train(str(ttr))
            logger.log_id_train_str('route')
            logger.log_id_start(str(te[0][0]))
            logger.log_id_end(str(te[0][1]))
            logger.log_clust_test(str(te[1]))
            logger.log_clust_train(str(tr[1]))
            logger.log_id_test(str(tte))
            logger.log_id_train(str(ttr))
            logger.log_sz_test(str(len(df_test)))
            logger.log_sz_train(str(len(df_train)))

            runLinModels(df_train, df_test, _prepData_LinModels, params)
            runClassifRegressModels(df_train, df_test, _prepData_ClassifRegressModels, params)
          
            logger.reset_all()
            print "Done"
            finished.write(str(te)+","+str(tr)+"\n")
            finished.flush()
    """

def calculate_shortest_path(df_test):
    sp = gmh.googleDistMatrixEst
    df_test['shortest_path_dist'] = df_test.apply(lambda row:sp((row['pick_lon'], row['pick_lat']), (row['drop_lon'], row['drop_lat']))[0], axis = 1)

    
#Training the model on the real distances, but testing on the shortes path distances obtained from Google API
def _prepData_LinModels(df_train, df_test):
   
    #Prepare model input for regression
    X_train = df_train['trip_distance'].values
    X_test = df_test['shortest_path_dist'].values

    y_train = df_train['trip_time_in_secs'].values
    y_test = df_test['trip_time_in_secs'].values

    return X_train, X_test, y_train, y_test

def _prepData_ClassifRegressModels(df_train, df_test):

    X_train = df_train[['trip_distance', 'weekday', 'hour']].values
    X_test = df_test[['shortest_path_dist', 'weekday', 'hour']].values

    y_train = df_train['trip_time_in_secs'].values
    y_test = df_test['trip_time_in_secs'].values

    return X_train, X_test, y_train, y_test