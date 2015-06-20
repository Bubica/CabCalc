import pandas as pd
import numpy as np
import datetime
import calendar
from ..geo import google_loc as gmaps



""" 
Module for data manipulation.
"""

def filter_percentile(df, col, up=95, down=5):
    """
    Return only subset with values inside the percentile range.
    """
    pup = np.percentile(df[col].values, up)
    pdw = np.percentile(df[col].values, down)

    s = (df[col]<pup) & (df[col]>pdw)
    df2 = df[s]

    return df2
    
def add_shortest_route(df):
    """
    Computes the distance of the shortest route beween pickup and dropoff points and adds additional column for the distance and duration.
    """

    df['gmaps_dist'] = df.apply(lambda row: gmaps.getTotDist((row['pick_lon'], row['pick_lat']), (row['drop_lon'], row['drop_lat'])), axis=1)
    df['gmaps_dur'] = df.apply(lambda row: gmaps.getTotDur((row['pick_lon'], row['pick_lat']), (row['drop_lon'], row['drop_lat'])),  axis=1)

def keep_weekends(df):
    #Filter out work days
    isweekend = lambda x: x.weekday() in [5,6]
    
    df2 = df[df.pick_date.map(isweekend)]
    df2 = df2[df2.drop_date.map(isweekend)]

    return df2

def keep_workdays(df):

    isworkday = lambda x: x.weekday() in [0,1,2,3,4]
    
    df2 = df[df.pick_date.map(isworkday)]
    df2 = df2[df2.drop_date.map(isworkday)]

    return df2

def keep_daytimes(df, hours=range(0,24)):
    """
    Filters out the entries that fall outside the given times
    times are defined in hours (0-23 h format)
    """
    within_hours = lambda x: x.hour in hours

    df2 = df[df.pick_date.map(within_hours)]
    df2 = df2[df2.drop_date.map(within_hours)]

    return df2

def keep_Manhattan(df):
    """
    Retains only entries that have start and end points on keep_Manhattan
    """
    
    df2 = df.apply(lambda row: gmaps.onManhattan(row['pick_lat'], row['pick_lon']), axis=1)
    df2 = df2.apply(lambda row: gmaps.onManhattan(row['drop_lat'], row['drop_lon']), axis=1)

    return df2


