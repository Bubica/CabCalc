import pandas as pd
import os
import itertools
import numpy as np

from ...geo import google_loc 
from .. import config
from val_predict import ValidationPredictor
import log
from ...trip_predict.predictor import location_aware
from ...trip_predict.predictor import all_routes

#Basic config stored in default.ini file


class Validator(object):
    
    """ 
    The main class for running a comprehensive validation procedure.
    A separate validation is preformed across the grid of parameter data and the result of each such 
    validation is stored in the output file.
    """

    def __init__(self, output_folder, predictor_module=location_aware):

        self.predictor = ValidationPredictor(predictor_module)
        self.predictor_module = predictor_module
        io_pref = predictor_module.__name__.split('.')[-1] #prefix for io files

        config_fname = os.path.dirname(__file__)+"/"+io_pref+"_config.ini"
        config.set_config_file(config_fname)

        print "Config file:", config_fname

        output_folder = output_folder if output_folder[-1]=='/' else output_folder+"/"
        output_fname = 'validation_results_' + io_pref +'.csv'
        self.logger = log.Logger(output_folder + output_fname) 

    def run(self):

        #Experimental setups incude varying number of sampes in the train/test dataset, geo area where the data is sampled from etc.
        #Model setups pertain to specific parameters of the chosen predicot module (learning rate, number of 
        #estimators in the composite predictors etc.)

        expSetups = loadExpSetups(self.predictor_module)
        modelSetups = loadModelSetups(self.predictor_module)

        self.logger.log_header()

        for is_ in range(len(expSetups)):

            #Update experimental setup - single data load for each model setup
            eSetup = expSetups.loc[is_]

            print "Running experimental setup ", is_

            for im_ in range(len(modelSetups)):

                mSetup = modelSetups.loc[im_]

                print "        Running  model setup "
                print mSetup

                #If previously logged - skip
                self.logger.set_setup(eSetup, mSetup)
                if self.logger.check_setup_logged():
                    print "SKIPPED"
                    continue

                self.predictor.updateExpSetup(eSetup)
                self.predictor.updateModelSetup(mSetup) #Update model setup
                results = self.predictor.run() #Train the model and store results

                #LOG results
                self.logger.set_results(results)
                self.logger.log() #push to file


def loadExpSetups(predictor_module):
    """
    Load all possible combinations of the experimental setups.
    These setups are applicable to all tested models.
    """   
    print "Loading experiment setups.... ",

    #Load data from default.ini config file - config file contains different experimental setups for training on the subset of data
    routes = config.load_routes()
    dates = config.load_dates()
    train_area, train_sample_cnt, train_time_interval = config.load_train_setup()
    test_area, test_time_interval = config.load_test_setup()
    estimator = ["trip_duration"]

    #create experiment setup dataframe
    expSetups = pd.DataFrame(columns = ['route', 'date', 'train_time_interval', 'test_time_interval', 'train_sample_cnt', 'train_area', 'test_area', 'estimator'])
    if predictor_module == location_aware:
        for i, val in enumerate(itertools.product(routes, dates, train_time_interval, test_time_interval, train_sample_cnt, train_area, test_area, estimator)):
            expSetups.loc[i] = list(val)
        


    elif predictor_module == all_routes:
        for i, val in enumerate(itertools.product(routes, dates, train_time_interval, test_time_interval, train_sample_cnt, [None], test_area, estimator)):
            expSetups.loc[i] = list(val)
        
    #Compute the size of test samples
    expSetups['test_sample_cnt'] = expSetups.train_sample_cnt.map(lambda train: int(3./7. * train)) #30/70 test/train ratio
    
    #Unpack route info
    expSetups["from"] = expSetups['route'].apply(lambda x: x[0])
    expSetups["to"] = expSetups['route'].apply(lambda x: x[1])
    del expSetups["route"]

    #Obtain route coordinates (if same point present in more that one route, do the resolution only once)
    loc_lonlat = {i : google_loc.getCoordFromAddress(i, True)[0] for i in np.unique(np.concatenate([expSetups['from'],expSetups['to']]))}

    expSetups['from_point'] = expSetups['from'].apply(lambda x: loc_lonlat[x])
    expSetups['to_point'] = expSetups['to'].apply(lambda x: loc_lonlat[x])

    print "Done!"
    return expSetups


def loadModelSetups(predictor_module):
    """ 
    Load all different model parameters used in validation
    """

    print "Loading model setups.... ",

    mp = _modelParams()
    modelSetups = pd.DataFrame(columns=["type", "n_estimators", "learn_rate", "max_samples", "max_depth"])

    mTypes = ['LIN', 'FLWS', 'BAG', 'FOREST', 'GRAD'] #types of models 
    setups_ = []

    for t in mTypes:
        mpT = {k:mp[k][t] for k in mp if t in mp[k]} #parameters set for this model type

        mpTName = mpT.keys() #names of parameters set for this model
        for mpTComb in itertools.product(*mpT.values()): #combination of values of prameters
            val = {k:v for k,v in zip(mpTName, mpTComb)}
            val['type'] = t #add the info about the type of the model

            setups_.append(val)
    
    modelSetups = pd.DataFrame(setups_) #create dataframe from the list of dictionaries, missing values set to NaN

    #Convert types
    f_conv2int = lambda x: np.nan if np.isnan(x) else int(x)
    modelSetups.max_samples     = modelSetups.max_samples.map(f_conv2int)
    modelSetups.n_estimators    = modelSetups.n_estimators.map(f_conv2int)
    modelSetups.max_depth       = modelSetups.max_depth.map(f_conv2int)
    
    return modelSetups

""" ***************************************************************************************************************************** """


def _modelParams():
    """ 
    Returns all different model parameters used in validation

    TODO - move to config file
    """
    model_params = {}
    model_params['n_estimators'] = {'FOREST':[10,50], 'GRAD': [50, 100, 500], 'BAG': [10, 50, 100, 500]}
    model_params['learn_rate'] = {'GRAD': [0.01, 0.1]}
    model_params['max_samples'] = {'BAG': [10, 100]}
    model_params['max_depth'] = {'FOREST':[None, 3, 7], 'GRAD': [ 3, 5, 7]}

    return model_params


def main():
    validator = Validator("/Users/bubica/Development/CODE/PROJECTS/InsightDataScience2014/Project/code/info/validation_results/", all_routes)
    return validator.run()
