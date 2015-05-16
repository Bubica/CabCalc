"""
Use all routes in the database to do the prediction.
"""

import pandas as pd
import db_handlers.local_mysql as db
import db_tripQueries as db_trip
import db_tripInserts as dbi
import trip_manip as tmanip
import geoloc
import numpy as np
import time
import datetime
import map_handler.gmaps as gmh 
from map_handler import osm
from matplotlib import pyplot as pp
import sys
import models.baggingRegress as model_bag
import models.linearRegress as model_lin
import models.feasibleWLS as model_fwls
import models.randomForest as model_forest
import models.gradientBoost as model_grad

from test_setup import *

#Names of tables & database
db_name = 'taxi'
host = 'localhost'
user = 'root'
passwrd = 'bubach16'

def init():
    global db
    global db_trip

    #Init db connection
    db.init(host, user, passwrd, db_name)
    db_trip.set_dbModule(db)

def rand_train_data(n_samples_train = 100000, months = range(2,5)):
    #Fetch random data (train) from db

    t_perf1 = time.time()
    df_train = db_trip.query_Random(n_samples_train, months = months, fareJoin = True)
    t_perf2 = time.time()

    print "Query time: ", t_perf2 - t_perf1 , "s"

    return df_train

def rand_test_data(n_samples_test = 10000):
    pass

def routes_test_data(n_samples_test = 10000, mile_dia = 0.3, t_s = t5, t_e = t5e, p_start = point2, p_end = point1):
    #Fetch test data - from the subset of routes
    df_test = db_trip.query_Routes(p_start, p_end, mile_dia, lonLat=True, date_span = (t_s, t_e), fareJoin = True) 
    return df_test

def _filter(df_train, df_test, day_hours = range(0,24)):
    #FILTER DATA

    #Setup
    weekend = True
    workday = True
    rain = None

    #Filter
    df_train_filt = df_train.copy()
    df_test_filt = df_test.copy()

    if weekend: #weekends only
        df_train_filt = tmanip.keep_weekends(df_train_filt)
        df_test_filt = tmanip.keep_weekends(df_test_filt)
        
    elif workday: #work days only
        df_train_filt = tmanip.keep_workdays(df_train_filt)
        df_test_filt = tmanip.keep_workdays(df_test_filt)

    if day_hours is not None and len(day_hours)>0:
        df_train_filt = tmanip.keep_daytimes(df_train_filt, day_hours)
        df_test_filt = tmanip.keep_daytimes(df_test_filt, day_hours)
        
    df_train_filt = tmanip.filter_percentile(df_train_filt, 'trip_distance', 95,5)
    df_test_filt = tmanip.filter_percentile(df_test_filt, 'trip_distance', 95,5)

    return df_train_filt, df_test_filt


def fit_dist_vs_time(fig_name):

    X_train = df_train_filt['trip_distance'].values
    X_test = df_test_filt['trip_distance'].values

    y_train = df_train_filt['trip_time_in_secs'].values
    y_test = df_test_filt['trip_time_in_secs'].values

    res = {} #prediction, rmse, r2, feature_priority

    res['BAG'] = model_bag.run(X_train, X_test, y_train, y_test)
    res['LIN'] = model_lin.run(X_train, X_test, y_train, y_test)
    res['FWLS'] = model_fwls.run(X_train, X_test, y_train, y_test)
    res['FOREST'] = model_forest.run(X_train, X_test, y_train, y_test)
    res['GRAD'] = model_grad.run(X_train, X_test, y_train, y_test)

    plot_dist_vs_time(res, X_test, y_test, "dist_vs_time")

    return res

def fit_fare_vs_dist_and_time():
    X_train = df_train_filt[['trip_distance', 'trip_time_in_secs']].values
    X_test = df_test_filt[['trip_distance', 'trip_time_in_secs']].values

    y_train = df_train_filt['total_wo_tip'].values
    y_test = df_test_filt['total_wo_tip'].values

    res = {} #prediction, rmse, r2, feature_priority
    res['BAG'] = model_bag.run(X_train, X_test, y_train, y_test)
    res['LIN'] = model_lin.run(X_train, X_test, y_train, y_test)
    #y_pred_FWLS, rmse_FWLS, r2_FWLS = model_fwls.run(X_train, X_test, y_train, y_test)
    res['FOREST'] = model_forest.run(X_train, X_test, y_train, y_test)
    res['GRAD'] = model_grad.run(X_train, X_test, y_train, y_test)

    plot_dist_vs_time(res, X_test[:,0], y_test, "fare_vs_time", x_lab = "Time (min)", y_lab = "Fare ($)")
    plot_dist_vs_time(res, X_test[:,1], y_test, "fare_vs_dist", x_lab = "Distance (miles)", y_lab = "Fare ($)")

    return res

def plot_dist_vs_time(res, X_test, y_test, fig_name, x_lab = "Time (min)", y_lab = "Distance (miles)"):
    # plot dist vs time
    fig = pp.gcf()

    sz = 1000
    ax = pp.subplot(311)
    pp.plot(X_test[:sz], y_test[:sz]/60., 'go', label="train", alpha=0.3)
    pp.ylabel(y_lab)

    ax = pp.subplot(311)
    pp.plot(X_test[:sz], y_test[:sz]/60., 'go', label="train", alpha=0.3)

    pp.plot(X_test[:sz], res['BAG'][0][:sz]/60., 'ro', label="predict_BAG")
    pp.plot(X_test[:sz], res['LIN'][0][:sz]/60., 'yo', label="predict_LIN")
    if 'FWLS' in res: pp.plot(X_test[:sz], res['FWLS'][0][:sz]/60., 'mo', label="predict_FWLS")
    pp.legend(bbox_to_anchor=(1.12, 1.05))
    pp.ylabel(y_lab)

    ax = pp.subplot(212)
    pp.plot(X_test[:sz], y_test[:sz]/60., 'go', label="train", alpha=0.3)
    pp.plot(X_test[:sz], res['FOREST'][0][:sz]/60., 'ro', label="predict_FOREST")
    pp.plot(X_test[:sz], res['GRAD'][0][:sz]/60., 'bo', label="predict_GRAD")

    pp.xlabel(x_lab)
    pp.ylabel(y_lab)

    pp.legend(bbox_to_anchor=(1.12, 1.05))

    fig.set_size_inches(12, 6)
    fig.savefig(fig_name+".png", dpi = 400)