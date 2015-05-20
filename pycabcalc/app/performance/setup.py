import datetime
import json
import ConfigParser
import os

config = ConfigParser.ConfigParser()
config.read(os.path.dirname(__file__)+"/"+"default.ini") #Use default config file in the current directory

"""
Generic experimental setup. Contains info about the routes and dates used for performance tests and model validation.
"""

def set_config_file(fname):
    #Change config file (from the efault one)
    global config
    print fname
    print
    config.read(fname)

def load_times():

    global config

    #load the reference time points
    time_str = [i for i in config.get('Dates','ref_dates').split('\n') if len(i)>0]
    times = [datetime.datetime.strptime(i, "%Y-%m-%d %H:%M:%S") for i in time_str]

    return times


def load_routes():

    global config
    # locations = [i for i in config.get('Geo','locations').split('\n') if len(i)>0] #not in use
    routes = [tuple(i.split(' - ')) for i in config.get('Geo','routes').split('\n') if len(i)>0]
    return routes


def load_train_setup():

    global config

    areas = json.loads(config.get('Train','area'))
    sample_sets = json.loads(config.get('Train','samples'))
    t_intervals = json.loads(config.get('Train','t_interval'))

    return areas, sample_sets, t_intervals

def load_test_setup():

    global config

    areas = json.loads(config.get('Test','area'))
    sample_sets = json.loads(config.get('Test','samples'))
    t_intervals = json.loads(config.get('Test','t_interval'))

    return areas, sample_sets, t_intervals