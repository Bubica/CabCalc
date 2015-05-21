import pandas as pd
import numpy as np
import datetime
import calendar
import time

import generic_predictor as gp

from ...geo import google_loc
from ..models import baggingRegress as model_bag
from ..models import linearRegress as model_lin
from ..models import feasibleWLS as model_fwls
from ..models import randomForest as model_forest
from ..models import gradientBoost as model_grad

"""
Use all routes in the database to do the prediction.
"""

class TripPredictor(gp.TripPredictor):

    search_area = 0.3 #area around start end point used for searching for train routes

    def __init__(self, model = model_grad, modelParams=pd.Series([]), limit = None, interval_sz=None):

        super(TripPredictor,self).__init__(model = model, modelParams=modelParams, limit = limit, interval_sz=interval_sz)

        if not limit: 
            self.limit = 100000 #default number of routes retrieved

    def _loadTrainData(self, date):

        tStart, tEnd = self._trainTimeInterval(date)
        self.train_df = self._loadData(tStart, tEnd, self.limit)

    def _loadData(self, ts, te, limit):

        """
        Loads the train data from the database.
        If the time interval falls out of 2013 time range, previous/subsequent year is replaced with data 
        from 2013 for the  corresponding months.
        """
        t1 = time.time()
        cols=['pick_date', 'trip_distance', 'trip_time_in_secs', 'total_wo_tip', 'precip_b'] #make sure columns match the ones defining search index in the database
        # cols = None

        td = (te - ts).days #interval in number of days

        if ts.year < 2013:
            s1 = datetime.datetime(2013,1, 1, 0, 0, 0)
            e1 = te
            cnt1 = int(self.limit * (e1-s1).days/(1.*td)) #not a true random, but will do...
            df1 = self.dbObj.query_Random(cnt1, date_span = (s1, e1), cols=cols)

            s2 = datetime.datetime(2013, ts.month, ts.day, ts.hour, ts.minute, ts.second)
            e2 = datetime.datetime(2013,12, 31, 23, 59, 59)
            cnt2 = self.limit - cnt1 
            df2 = self.dbObj.query_Random( cnt2, date_span = (s2, e2), cols=cols)

            df = pd.concat([df1, df2], axis = 0)

        elif te.year > 2013:
            s1 = ts
            e1 = datetime.datetime(2013,12, 31, 23, 59, 59)
            cnt1 = int(self.limit * (e1-s1).days/(1.*td))#not a true random, but will do...
            df1 = self.dbObj.query_Random(cnt1, date_span = (s1, e1), cols=cols)

            s2 = datetime.datetime(2013,1, 1, 0, 0, 0)
            e2 = datetime.datetime(2013, te.month, te.day, te.hour, te.minute, te.second)
            cnt2 = self.limit - cnt1 
            df2 = self.dbObj.query_Random( cnt2, date_span = (s2, e2), cols=cols)

            df = pd.concat([df1, df2], axis = 0)

        else:
            df = self.dbObj.query_Random(self.limit, date_span = (ts,te), cols=cols)

        #Add additional features
        self._addFeatures(df)

        return df

    def getEstimates(self, s_point, e_point, date):

        """
        Input: 
        start and end locations of the taxi ride (in lon/lat format)
        dist: distance between these two points (estimate of the average route)
        date when the taxi trip will be taken
        """

        ts = time.time() #start timer

        self._loadTrainData(date)

        dist = google_loc.getDistance(s_point, e_point)[0] #get an estimate of the distance between these two points
        durEst = self._estDuration(dist, date)
        fareEst = self._estFare (dist, date)

        te = time.time()
        t_delta = te - ts

        return durEst, fareEst, t_delta


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