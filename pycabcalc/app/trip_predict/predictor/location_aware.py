import pandas as pd
import numpy as np
import datetime
import calendar
import time

import generic_predictor as gp

from .. import manip

from ...geo import google_loc
from ..models import baggingRegress as model_bag
from ..models import linearRegress as model_lin
from ..models import feasibleWLS as model_fwls
from ..models import randomForest as model_forest
from ..models import gradientBoost as model_grad

class TripPredictor(gp.TripPredictor):

    search_area = 0.3 #area around start end point used for searching for train routes
    min_train_sample_size = 100 #min number of samples needed to build a model

    def __init__(self, model = model_grad, modelParams=pd.Series([]), limit = None, search_area=None, interval_sz=None):

        super(TripPredictor,self).__init__(model = model, modelParams=modelParams, limit = limit, interval_sz=interval_sz)

        if search_area: 
            self.search_area = search_area

    def _loadTrainData(self, date, s_point, e_point):

        tStart, tEnd = self._trainTimeInterval(date)
        self.train_df = self._loadData(tStart, tEnd, s_point, e_point, self.search_area, self.limit)

    def _loadData(self, ts, te, s_point, e_point, env_sz, limit, cols = ['pick_date', 'trip_distance', 'trip_time_in_secs', 'total_wo_tip', 'precip_f']):

        """
        Loads the train data from the database.
        If the time interval falls out of 2013 time range, previous/subsequent year is replaced with data 
        from 2013 for the  corresponding months.
        """
        t1 = time.time()

        td = (te - ts).days #interval in number of days

        if ts.year < 2013:
            s1 = datetime.datetime(2013,1, 1, 0, 0, 0)
            e1 = te
            cnt1 = None if limit is None else int(limit * (e1-s1).days/(1.*td))
            df1 = self.dbObj.query_Routes(s_point, e_point, env_sz = env_sz, date_span = (s1, e1), limit=cnt1, cols=cols, random=True)

            s2 = datetime.datetime(2013, ts.month, ts.day, ts.hour, ts.minute, ts.second)
            e2 = datetime.datetime(2013,12, 31, 23, 59, 59)
            cnt2 = None if limit is None else limit - cnt1
            df2 = self.dbObj.query_Routes(s_point, e_point, env_sz = env_sz, date_span = (s2, e2), limit=cnt2, cols=cols, random=True)

            df = pd.concat([df1, df2], axis = 0)

        elif te.year > 2013:
            s1 = ts
            e1 = datetime.datetime(2013,12, 31, 23, 59, 59)
            cnt1 = None if limit is None else int(limit * (e1-s1).days/(1.*td))
            df1 = self.dbObj.query_Routes(s_point, e_point, env_sz = env_sz, date_span = (s1, e1), limit=cnt1, cols=cols, random=True)

            s2 = datetime.datetime(2013,1, 1, 0, 0, 0)
            e2 = datetime.datetime(2013, te.month, te.day, te.hour, te.minute, te.second)
            cnt2 = None if limit is None else limit - cnt1
            df2 = self.dbObj.query_Routes(s_point, e_point, env_sz = env_sz, date_span = (s2, e2), limit=cnt2, cols=cols, random=True)

            df = pd.concat([df1, df2], axis = 0)
        
        else:
            df = self.dbObj.query_Routes(s_point, e_point, env_sz = env_sz, date_span = (ts,te), limit=limit, cols=cols, random=True)

        if len(df) < self.min_train_sample_size:
            #No records found - raise exeption
            raise InsufficientDataError("No train data found.")

        #Crude way of removing outliers
        df = manip.filter_percentile(df, 'trip_distance', 95,5)

        #Add additional features
        df = self._addFeatures(df)

        return df

    def getEstimates(self, s_point, e_point, date):

        """
        Input: 
        start and end locations of the taxi ride (in lon/lat format)
        date when the taxi trip will be taken
        """

        ts = time.time() #start timer

        self._loadTrainData(date, s_point, e_point)

        dist = google_loc.getDistance(s_point, e_point)[0] #get an estimate of the distance between these two points
        
        durEst_norain = self._estDuration(dist, date, rain = False)
        durEst_rain   = self._estDuration(dist, date, rain = True)
        
        fareEst_norain = self._estFare (dist, date, rain = False)
        fareEst_rain   = self._estFare (dist, date, rain = True)

        te = time.time()
        t_delta = te - ts

        return durEst_norain, fareEst_norain, durEst_rain, fareEst_rain, t_delta


class InsufficientDataError(Exception):

    def __init__(self, message):
        super(InsufficientDataError, self).__init__(message)


