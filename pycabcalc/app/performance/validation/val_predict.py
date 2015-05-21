from collections import defaultdict
from ..geo import google_loc as google_loc 
from ..geo import tools as geotools

from ..trip_predict.predictor import generic_predictor as gp
from ..trip_predict.predictor import location_aware
from ..trip_predict.predictor import all_routes

from ..predict.models import baggingRegress as model_bag
from ..predict.models import linearRegress as model_lin
from ..predict.models import feasibleWLS as model_fwls
from ..predict.models import randomForest as model_forest
from ..predict.models import gradientBoost as model_grad

class ValidationPredictor(gp.TripPredictor):

    """ 
    Tweaked verison on TripPredictor used for running validation tests.
    The instances of this class enable a single load of train data and running the validation on different models.
    """

    def __init__(self, predictor_module=location_aware):

        self.native_predictor = predictor_module.TripPredictor() #native load data used

        #stores info about previously loaded data to avoid reloading the same dataset
        self.prevLoaded = None

    def updateExpSetup(self, expSetup):
        self.expSetup  = expSetup

        #Load new data for train/test purpose
        self._loadTrainData()
        self._loadTestData()
        self.prevLoaded = self.expSetup.copy(deep=True) #store info about loaded data


    def updateModelSetup(self, modelSetup):
        self.modelSetup  = modelSetup
        params = self.modelSetup.drop('type') #model params
        typ = self.modelSetup['type']

        #string type of the model
        if typ == "BAG":
            self._setModel(model_bag, params)
        if typ == "LIN":
            self._setModel(model_lin, params)
        if typ == "FLWS":
            self._setModel(model_fwls, params)
        if typ == "FOREST":
            self._setModel(model_forest, params)
        if typ == "GRAD":
            self._setModel(model_grad, params)

    def _loadTrainData(self):
        if not self.prevLoaded \
            or self.prevLoaded['train_time_interval'] != self.expSetup['train_time_interval'] \
            or self.prevLoaded['train_area'] != self.expSetup['train_area'] \
            or self.prevLoaded['from_point'] != self.expSetup['from_point'] \
            or self.prevLoaded['to_point'] != self.expSetup['to_point'] \
            or self.prevLoaded['date'] != self.expSetup['date'] \
            or self.prevLoaded['train_sample_cnt'] != self.expSetup['train_sample_cnt']:

            #Using past observations to infer trip durations of future trips
            tStart, tEnd  = self._timeInterval(self.expSetup['date'], self.expSetup['train_time_interval'], "end")
            self.train_df = self.native_predictor._loadData(tStart, tEnd, self.expSetup['from_point'], self.expSetup['to_point'], self.expSetup['train_area'], self.expSetup['train_sample_cnt']) 

    def _loadTestData(self):
        if not self.prevLoaded \
            or self.prevLoaded['test_time_interval'] != self.expSetup['test_time_interval'] \
            or self.prevLoaded['test_area'] != self.expSetup['test_area'] \
            or self.prevLoaded['from_point'] != self.expSetup['from_point'] \
            or self.prevLoaded['to_point'] != self.expSetup['to_point'] \
            or self.prevLoaded['date'] != self.expSetup['date'] \
            or self.prevLoaded['test_sample_cnt'] != self.expSetup['test_sample_cnt']:

            #Using past observations to infer trip durations of future trips
            tStart, tEnd = self._timeInterval(self.expSetup['date'], self.expSetup['test_time_interval'], "start")
            self.test_df = self.native_predictor._loadData(tStart, tEnd, self.expSetup['from_point'], self.expSetup['to_point'], self.expSetup['test_area'], self.expSetup['test_sample_cnt'])
            self._shortest_route(self.test_df)

    def _shortest_route(self, df):
        """
        Computes shortest route for each entry in the dataframe.
        """
        sp = google_loc.googleDistMatrixEst
        toLonLatPair = lambda px, py, dx, dy: (geotools.toLonLat(px, py), geotools.toLonLat(dx, dy)) #hack since double unpacking with asterisk does not work
        df['shortest_route_dist'] = df.apply(lambda row: sp(*toLonLatPair(row['pick_x'], row['pick_y'], row['drop_x'], row['drop_y']))[0], axis = 1)

    def run(self):

        """
        Use the given data to train the model and return the predicted trip duration value for the requested input (dist, date).
        """

        if not all(k in self.train_df.columns for k in ['pick_date', 'trip_distance', 'trip_time_in_secs']):
            raise ValueError ("Train data frame is missing columns needed for constructing the model!")

        #Compose the features
        if self.modelType in ["LIN", "FLWS", "BAG"]:
            features_train = ['trip_distance', 'min']
            features_test  = ['shortest_route_dist', 'min']

        elif self.modelType in ["FOREST", "GRAD"]:

            #Separate categorical from numerical features
            numerical_features_train = ['trip_distance', 'min', 'precip_f', 'weekend']
            numerical_features_test = ['shortest_route_dist', 'min', 'precip_f', 'weekend']
            categorical_features =  ['tod_midday', 'tod_afternoon', 'tod_evening', 'tod_night', 'weekday_1', 'weekday_2', 'weekday_3', 'weekday_4', 'weekday_5', 'weekday_6']

            features_train = list(itertools.chain(numerical_features_train, categorical_features))
            features_test = list(itertools.chain(numerical_features_test, categorical_features))


        output = 'trip_time_in_secs'

        X_train = self.train_df[features_train].values
        y_train = self.train_df[output].values

        X_test = self.test_df[features_test].values
        y_test = self.test_df[output].values

        results = defaultdict()
        _, results['rmse'], results['r2'], feat_priority = self.model.run(X_train, X_test, y_train, y_test, **self.modelParams) 
        results['fe'] = None if not feat_priority else ','.join([features[i] for i in feat_priority[:5]]) #store 5 most prominent features in a string

        return results
