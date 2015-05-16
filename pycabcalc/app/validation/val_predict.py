from .. import manip
from ..predict.predict import TripPredictor
from collections import defaultdict
from ..db.taxiDB import TripQ
from ..geo import google_loc as google_loc 
from ..geo import basic as geoloc

from ..predict.models import baggingRegress as model_bag
from ..predict.models import linearRegress as model_lin
from ..predict.models import feasibleWLS as model_fwls
from ..predict.models import randomForest as model_forest
from ..predict.models import gradientBoost as model_grad

class ValidationPredictor(TripPredictor):

    """ 
    Tweaked verison on TripPredictor used for running validation tests.
    The instances of this class enable a single load of train data and running the validation on different models.
    """

    def __init__(self):
        self.dbObj = TripQ()

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
            or self.prevLoaded['trainInt'] != self.expSetup['trainInt'] \
            or self.prevLoaded['trainArea'] != self.expSetup['trainArea'] \
            or self.prevLoaded['from_point'] != self.expSetup['from_point'] \
            or self.prevLoaded['to_point'] != self.expSetup['to_point'] \
            or self.prevLoaded['date'] != self.expSetup['date'] \
            or self.prevLoaded['trainSmpl'] != self.expSetup['trainSmpl']:

            tStart, tEnd = self._timeInterval(self.expSetup['date'], self.expSetup['trainInt'], "end")
            self.train_df = self._loadData(tStart, tEnd, self.expSetup['from_point'], self.expSetup['to_point'], self.expSetup['trainArea'], self.expSetup['trainSmpl']) 

            #Crude way of removing outliers
            manip.filter_percentile(self.train_df, 'trip_distance', 95,5)

    def _loadTestData(self):
        if not self.prevLoaded \
            or self.prevLoaded['testInt'] != self.expSetup['testInt'] \
            or self.prevLoaded['testArea'] != self.expSetup['testArea'] \
            or self.prevLoaded['from_point'] != self.expSetup['from_point'] \
            or self.prevLoaded['to_point'] != self.expSetup['to_point'] \
            or self.prevLoaded['date'] != self.expSetup['date'] \
            or self.prevLoaded['testSmpl'] != self.expSetup['testSmpl']:

            tStart, tEnd = self._timeInterval(self.expSetup['date'], self.expSetup['testInt'], "start")
            self.test_df = self._loadData(tStart, tEnd, self.expSetup['from_point'], self.expSetup['to_point'], self.expSetup['testArea'], self.expSetup['testSmpl'])
            self._shortest_route(self.test_df)

            #Crude way of removing outliers
            manip.filter_percentile(self.test_df, 'trip_distance', 95,5)

    def _shortest_route(self, df):
        """
        Computes shortest route for each entry in the dataframe.
        """
        sp = google_loc.googleDistMatrixEst
        toLonLatPair = lambda px, py, dx, dy: (geoloc.toLonLat(px, py), geoloc.toLonLat(dx, dy)) #hack since double unpacking with asterisk does not work
        df['shortest_route_dist'] = df.apply(lambda row: sp(*toLonLatPair(row['pick_x'], row['pick_y'], row['drop_x'], row['drop_y']))[0], axis = 1)

    def run(self):

        """
        Use the given data to train the model and return the predicted trip duration value for the requested input (dist, date).
        """

        if not all(k in self.train_df.columns for k in ['pick_date', 'trip_distance', 'trip_time_in_secs']):
            raise ValueError ("Train data frame is missing columns needed for constructing the model!")

        #Compose the features
        if self.modelType in ["LIN", "FLWS", "BAG"]:
            featuresTrain = ['trip_distance']
            featuresTest  = ['shortest_route_dist']

        elif self.modelType in ["FOREST", "GRAD"]:
            featuresTrain = ['trip_distance', 'weekday', 'hour']
            featuresTest  = ['shortest_route_dist', 'weekday', 'hour']

        output = 'trip_time_in_secs'

        X_train = self.train_df[featuresTrain].values
        y_train = self.train_df[output].values

        X_test = self.test_df[featuresTest].values
        y_test = self.test_df[output].values

        results = defaultdict()
        _, results['rmse'], results['r2'], results['fe'] = self.model.run(X_train, X_test, y_train, y_test, **self.modelParams) 
    
        return results
