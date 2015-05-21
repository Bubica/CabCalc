"""
Defines the generic behaviour of TripPredictor instance.
"""
import pandas as pd
import numpy as np
import datetime

from ...db.taxiDB import TripQ
from ...geo import google_loc
from ..models import baggingRegress as model_bag
from ..models import linearRegress as model_lin
from ..models import feasibleWLS as model_fwls
from ..models import randomForest as model_forest
from ..models import gradientBoost as model_grad

class TripPredictor(object):

    interval_sz = 60 #size of the train interval in the number of days
    limit = None #max no of records to retrieve in a single transaction

    def __init__(self, model = model_grad, modelParams=pd.Series([]), limit = None, interval_sz=None):
        self._setModel(model, modelParams)
        self.dbObj = TripQ()

        self.limit = limit 

        if interval_sz: self.interval_sz = interval_sz


    def _setModel(self, model, modelParams):
        self.model = model #model used for the estimation

        self.modelParams = modelParams
        if type(self.modelParams) is pd.core.frame.Series:
            self.modelParams = self.modelParams.dropna().to_dict()
        

        #string type of the model
        if self.model == model_bag:
            self.modelType = "BAG"
        if self.model == model_lin: 
            self.modelType = "LIN"
        if self.model == model_fwls:
            self.modelType = "FLWS"
        if self.model == model_forest:
            self.modelType = "FOREST"
        if self.model == model_grad:
            self.modelType = "GRAD"

    def _trainTimeInterval(self, date, date_point="end"):

        """ Training on the previous observations """
        return self._timeInterval (date, self.interval_sz, date_point)

    def _timeInterval(self, date, interval_sz, date_point):

        """
        Interval of days taken from the database to train the model.
        date_point: the train interval will either be centered around the given date ("middle") or end with this date ("end") or start with this date
        """
        if date_point == "middle":
            t_2013_middle =  datetime.datetime(2013, date.month, date.day, date.hour, date.minute, date.second)
            t_2013_end   = t_2013_middle + datetime.timedelta(days = interval_sz/2) #do not include the requested day
            t_2013_start = t_2013_middle -  datetime.timedelta(days = interval_sz/2)

        elif date_point == "end":
            t_2013_end =  datetime.datetime(2013, date.month, date.day, date.hour, date.minute, date.second)
            t_2013_end = t_2013_end - datetime.timedelta(days=1) #do not include the requested day
            t_2013_start = t_2013_end -  datetime.timedelta(days = interval_sz)

        elif date_point == "start":
            t_2013_start = datetime.datetime(2013, date.month, date.day, date.hour, date.minute, date.second)
            t_2013_end = t_2013_start + datetime.timedelta(days = interval_sz)

        else:
            raise ValueError("Incorrect date_point type!")

        print
        print "Start time", t_2013_start, "end time", t_2013_end
        print
        
        return (t_2013_start, t_2013_end)
    
    def _addFeatures(self, df):
        
        #Add additional features to train/test dataframe
        if len(df)>0:
            df['weekday'] = df.apply(lambda row: row['pick_date'].weekday(), axis=1) 
            df['is_weekend'] = df.apply(lambda row: 1 if row['weekday'] in [5,6] else 0, axis=1) 
            df['is_morning'] = df.apply(lambda row: 1 if row['pick_date'].hour in [7,8,9,10] else 0, axis=1) 
            df['is_midday'] = df.apply(lambda row: 1 if row['pick_date'].hour in [11,12,] else 0, axis=1) 

            df['hour'] = df.apply(lambda row: row['pick_date'].hour, axis=1)

    def _estDuration(self, dist, date):

        """
        Use the given data to train the model and return the predicted trip duration value for the requested input (dist, date).
        """

        if not all(k in self.train_df.columns for k in ['pick_date', 'trip_distance', 'trip_time_in_secs']):
            raise ValueError ("Input data frame is missing columns needed for construcing the model!")

        #Compose the features
        if self.modelType in ["LIN", "FLWS", "BAG"]:
            features = ['trip_distance']
        elif self.modelType in ["FOREST", "GRAD"]:
            features = ['trip_distance', 'weekday', 'hour']

        output = 'trip_time_in_secs'

        X_train = self.train_df[features].values
        y_train = self.train_df[output].values

        X_test = np.array([[dist, date.weekday(), date.hour]])
        y_test = [10] #Not in use

        y_pred, _,_,_ = self.model.run(X_train, X_test, y_train, y_test, **self.modelParams) 
        est = round(y_pred[0]/60., 2) #convert to minutes

        return est

    def _estFare(self, dist, date):
              
        """
        Use the given data to train the model and return the predicted fare value for the requested input (dist, date).
        """

        if not all(k in self.train_df.columns for k in ['pick_date', 'trip_distance', 'total_wo_tip']):
            raise ValueError ("Input data frame is missing columns needed for construcing the model!")

        #Compose the features
        if self.modelType in ["LIN", "FLWS", "BAG"]:
            features = ['trip_distance']
        elif self.modelType in ["FOREST", "GRAD"]:
            features = ['trip_distance', 'weekday', 'hour']

        output = 'total_wo_tip'

        X_train = self.train_df[features].values
        y_train = self.train_df[output].values

        X_test = np.array([[dist, date.weekday(), date.hour]])
        y_test = [10] #Not in use 

        y_pred, _,_, _ = self.model.run(X_train, X_test, y_train, y_test, **self.modelParams) 
        est = round(y_pred[0], 2)

        return est
