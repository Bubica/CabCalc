"""
Defines the generic behaviour of TripPredictor instance.
"""
import pandas as pd
import numpy as np
import datetime
import itertools

from sklearn.preprocessing import OneHotEncoder

from ...db.taxiDB import TripQ
from ...geo import google_loc
from ..models import baggingRegress as model_bag
from ..models import linearRegress as model_lin
from ..models import feasibleWLS as model_fwls
from ..models import randomForest as model_forest
from ..models import gradientBoost as model_grad


#Util functions
f_is_weekend = lambda date: 1 if date.weekday() in [5,6] else 0

def f_tod(date): 
    #time of the day
    if date.hour in [6,7,8,9,10]: return "morning"
    if date.hour in [11,12,13,14]: return "midday"
    if date.hour in [15,16,17,18]: return "afternoon"
    if date.hour in [19, 20, 21, 22, 23]: return "evening"
    if date.hour in [0, 1, 2, 3, 4, 5]: return "night"


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

            df = df.reset_index()

            df['hour'] = df.apply(lambda row: row['pick_date'].hour, axis=1)
            df['min']  = df.apply(lambda row: row['pick_date'].hour * 60 + row['pick_date'].minute, axis=1)
            df['weekend'] = df.apply(lambda row: f_is_weekend(row['pick_date']), axis=1) #binary feature
            tod = df.apply(lambda row: f_tod(row['pick_date']), axis=1) #morning, midday, afternoon, envening, night
            weekday = df.apply(lambda row: row['pick_date'].weekday(), axis=1)  #0-6

            #dummify categorical features (drop one dummy and append the rest to the resulting dataframe)
            #append referent values to interim data to make sure all columns are present in the output (even if dataset does not
            #contain all values in tod/weekday column)
            ref_vals = ['morning', 'midday', 'afternoon', 'evening', 'night']
            tod = pd.Series(list(itertools.chain(tod, ref_vals))) 
            tod = pd.get_dummies(tod, prefix = 'tod')
            df = df.join(tod.ix[:len(df), ['tod_'+i for i in ref_vals[1:]]])

            ref_vals = range(0,7)
            weekday = pd.Series(list(itertools.chain(weekday, ref_vals)))
            weekday = pd.get_dummies(weekday, prefix = 'weekday')
            df = df.join(weekday.ix[:len(df), ['weekday_'+str(i) for i in ref_vals[1:]]])

        return df


    def _est(self, dist, date, output_col, rain = False):

        """
        Use the given data to train the model and return the predicted trip duration value for the requested input (dist, date).
        """

        if not all(k in self.train_df.columns for k in ['pick_date', 'trip_distance', 'trip_time_in_secs']):
            raise ValueError ("Input data frame is missing columns needed for construcing the model!")

        #Compose the features
        if self.modelType in ["LIN", "FLWS", "BAG"]:
            features = ['trip_distance', 'min']

            #simple test dataset (all numerical features)
            X_test = np.array([[dist, date.hour*60 + date.minute]])

        elif self.modelType in ["FOREST", "GRAD"]:

            #Separate categorical from numerical features
            numerical_features = ['trip_distance', 'min', 'precip_f', 'weekend']
            categorical_features =  ['tod_midday', 'tod_afternoon', 'tod_evening', 'tod_night', 'weekday_1', 'weekday_2', 'weekday_3', 'weekday_4', 'weekday_5', 'weekday_6']
            features = list(itertools.chain(numerical_features, categorical_features))

            precip = 0 if not rain else 1 #Rain float value
            df_test = pd.DataFrame([[date, dist, precip]], columns = ['pick_date', 'trip_distance', 'precip_f'])
            df_test = self._addFeatures(df_test)
            X_test = df_test[features].values
            

        X_train = self.train_df[features].values
        y_train = self.train_df[output_col].values
        y_test = [10] #Not in use

        y_pred, _,_, fi = self.model.run(X_train, X_test, y_train, y_test, **self.modelParams) 

        if fi is not None: 
            print "FEATURES: cnt", X_train.shape[1], " importance order", [features[i] for i in fi]
        return y_pred[0]

    def _estDuration(self, dist, date, rain = False):

        e = self._est(dist,date, output_col='trip_time_in_secs', rain = rain)
        e = round(e/60., 2) #convert trip duration to minutes

        return e

    def _estFare(self, dist, date, rain = False):
              
        """
        Use the given data to train the model and return the predicted fare value for the requested input (dist, date).
        """

        est = self._est(dist,date, output_col='total_wo_tip', rain = rain)
        est = round(est, 2)

        return est

