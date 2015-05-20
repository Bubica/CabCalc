from ..geo import google_loc as gmh 
import datetime
import calendar
import random
import itertools
import pandas as pd
import numpy as np

def loadExpSetups():
    """
    Load all possible combinations of the experimental setups.
    These setups are applicable to all tested models.
    """   
    print "Loading experiment setups.... ",

    routes = _routes()
    refDates, trainInt, testInt = dates()
    trainSmpl, testSmpl = sampleNo()
    estTyp = _estimatorType()
    trainArea, testArea = areas()

    expSetups = pd.DataFrame(columns = ['route', 'date', 'trainInt', 'testInt', 'trainSmpl', 'testSmpl', 'trainArea', 'testArea', 'estTyp'])

    for i, val in enumerate(itertools.product(routes, refDates, trainInt, testInt, trainSmpl, testSmpl, trainArea, testArea, estTyp)):
        expSetups.loc[i] = list(val)

    #Unpack route info
    expSetups["from"] = expSetups['route'].apply(lambda x: x[0])
    expSetups["to"] = expSetups['route'].apply(lambda x: x[1])
    del expSetups["route"]

    #Obtain route coordinates
    loc_lonlat = {i : gmh.getCoordFromAddress(i) for i in np.unique(np.concatenate([expSetups['from'],expSetups['to']]))}

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

    print "Done!"
    return modelSetups

""" ***************************************************************************************************************************** """

def dates():
    """
    Define validation times used in the validation to compose the training set of points.
    """
    t1 = datetime.datetime(2013, 3, 1, 0, 0, 0) # 4 predefined reference dates
    t2 = datetime.datetime(2013, 6, 1, 0, 0, 0)
    t3 = datetime.datetime(2013, 9, 1, 0, 0, 0)
    t4 = datetime.datetime(2013, 12, 1, 0, 0, 0)

    refDates = [t1,t2,t3, t4]
    tIntTrain = [30, 60, 90, 120] #length of train interval (expressed in the number of days)
    tIntTest = [30]
    return refDates, tIntTrain, tIntTest


def _routes():
    """
    Returns list of tuples (start/end) representing routes used in the validation process.
    All combinations in locations list is present in the returned collection of routes.
    """
    #Locations used for defining routes used in validation process
    locations = {}
    locations[0]    = "Union Sq, NYC, USA"
    locations[1]    = "Times Sq, NYC, USA"
    locations[2]    = "Grand Central, NYC, USA"
    locations[3]    = "Chinatown, NYC, USA"
    locations[4]    = "Columbia University, NYC, USA"
    locations[5]    = "Harlem, New York, NYC, USA"
    locations[6]    = "Metropolitan Hospital, NYC, USA"
    locations[7]    = "11 Wall street, NYC, USA"
    locations[8]    = "59 St Columbus Circle, NYC, USA"
    locations[9]    = "Metropolitan Museum, 5th Avenue, New York, NYC, USA"
    locations[10]   = "4 Pennsylvania Plaza, NYC, USA" #Madison Square Garden
    locations[11]   = "Empire State Building, NYC, USA"

    #select all combinations of locations for validation
    # routes = []
    # for l1 in range(0, len(locations)-1):
    #     for l2 in range(l1, len(locations]):
    #         routes.append([locations[l1], locations[l2]])
    #         routes.append([locations[l2], locations[l1]])

    #preselect 15 routes for validation
    routes = []
    routes.append([locations[0], locations[1]])
    routes.append([locations[1], locations[0]])
    routes.append([locations[2], locations[1]])
    routes.append([locations[2], locations[0]])
    routes.append([locations[0], locations[2]])
    routes.append([locations[1], locations[2]])
    routes.append([locations[2], locations[4]])
    routes.append([locations[4], locations[2]])
    routes.append([locations[0], locations[7]])
    routes.append([locations[1], locations[7]])
    routes.append([locations[0], locations[1]])
    routes.append([locations[9], locations[0]])
    routes.append([locations[0], locations[9]])
    routes.append([locations[0], locations[5]])
    routes.append([locations[5], locations[0]])


    return routes

def areas():
    #The largest value of train area denotes approach of using all routes in the database for training
    trainA = [0.3,0.8,2,1000000] 
    testA = [0.3]

    return trainA, testA

def sampleNo():
    #No of samples used in train/test dataset
    train_samples = [100]#[100000] # TODO remove temp max no of samples in train/test set
    test_samples = [15] #[10000]

    return train_samples, test_samples

def estimatorType():
    return ['dist'] #'fare'

def modelParams():
    """ 
    Returns all different model parameters used in validation
    """
    model_params = {}
    model_params['n_estimators'] = {'FOREST':[10,50], 'GRAD': [50, 100, 500], 'BAG': [10, 50, 100, 500]}
    model_params['learn_rate'] = {'GRAD': [0.01, 0.1]}
    model_params['max_samples'] = {'BAG': [10, 100, 500, 1000]}
    model_params['max_depth'] = {'FOREST':[-1, 3, 7], 'GRAD': [ 3, 5, 7]}

    return model_params