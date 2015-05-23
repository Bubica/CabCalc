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
config_fname = os.path.dirname(__file__)+"/"+"default.ini"
config.set_config_file(config_fname)

class Validator(object):
    
    """ Main class for running the validation """

    def __init__(self, output_folder, predictor_module=location_aware):

        self.predictor = ValidationPredictor(predictor_module)

        output_folder = output_folder if output_folder[-1]=='/' else output_folder+"/"
        output_fname = 'validation_results_' + predictor_module.__name__.split('.')[-1]+'.csv'
        self.logger = log.Logger(output_folder + output_fname) 

    def run(self):

        expSetups = loadExpSetups()
        modelSetups = loadModelSetups()

        for is_ in range(len(expSetups)):

            #Update experimental setup - single data load for each model setup
            eSetup = expSetups.loc[is_]
            self.predictor.updateExpSetup(eSetup)

            print "Running experimental setup ", is_

            for im_ in range(len(modelSetups)):

                mSetup = modelSetups.loc[im_]

                print "        Running  model setup "
                print mSetup
                print eSetup.test_sample_cnt, eSetup.train_sample_cnt

                #If previously logged - skip
                self.logger.set_setup(eSetup, mSetup)
                # if self.logger.check_setup_logged():
                #     print "SKIPPED"
                #     continue

                self.predictor.updateModelSetup(mSetup) #Update model setup
                results = self.predictor.run() #Train the model and store results

                # if mSetup['type'] == "BAG":
                #     print "Grid", results == None
                #     return results

                #LOG results
                self.logger.set_results(results)
                self.logger.log() #push to file


def loadExpSetups():
    """
    Load all possible combinations of the experimental setups.
    These setups are applicable to all tested models.
    """   
    print "Loading experiment setups.... ",

    #Load data from default.ini config file
    locations = config.load_locations()
    routes = config.load_routes()
    dates = config.load_dates()
    train_area, train_sample_cnt, train_time_interval = config.load_train_setup()
    test_area, test_time_interval = config.load_test_setup()
    estimator = ["trip_duration"]

    #create experiment setup dataframe
    expSetups = pd.DataFrame(columns = ['route', 'date', 'train_time_interval', 'test_time_interval', 'train_sample_cnt', 'train_area', 'test_area', 'estimator'])

    # return dates, routes, train_time_interval, test_time_interval, train_sample_cnt, train_area, test_area

    for i, val in enumerate(itertools.product(routes, dates, train_time_interval, test_time_interval, train_sample_cnt, train_area, test_area, estimator)):
        expSetups.loc[i] = list(val)
    

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


def loadModelSetups():
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
    validator = Validator("/Users/bubica/Development/CODE/PROJECTS/InsightDataScience2014/Project/code/info/validation_results/", location_aware)
    return validator.run()
