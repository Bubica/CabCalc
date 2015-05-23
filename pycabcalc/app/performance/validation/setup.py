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