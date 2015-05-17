"""
Script for plotting different aspects of the trip data.
"""

from matplotlib import pyplot as pp
import matplotlib.colors as colors
import matplotlib.cm as cm

import pandas as pd
import numpy as np
import calendar

# import trip_manip as manip 
from ..db import taxiDB

# def weekends(df, xaxis_col, yaxis_col, size=100000):

#     df_weekend = manip.keep_weekends(df)
#     df_workday = manip.keep_workdays(df)
    
#     x_data_weekend = df_weekend[xaxis_col].values[:size]
#     y_data_weekend = df_weekend[yaxis_col].values[:size]

#     x_data_workday = df_workday[xaxis_col].values[:size]
#     y_data_workday = df_workday[yaxis_col].values[:size]

#     fig = pp.gcf()
#     pp.plot(x_data_weekend, y_data_weekend, 'go', label="weekend", alpha=0.1)
#     pp.plot(x_data_workday, y_data_workday, 'ro', label="workday", alpha=0.1)

#     pp.xlabel(xaxis_col)
#     pp.ylabel(yaxis_col)
#     pp.legend()

#     fig.savefig("weekends.png", dpi = 400)

# df['is_weekend'] = df.apply(lambda row: 1 if row['weekday'] in [5,6] else 0, axis=1) 
#         df['is_morning'] = df.apply(lambda row: 1 if row['pick_date'].hour in [7,8,9,10] else 0, axis=1) 
#         df['is_midday'] = df.apply(lambda row: 1 if row['pick_date'].hour in [11,12,] else 0, axis=1) 

def weekends(df, xaxis_col, yaxis_col, size=100000):

    _prepFeatures(df)    
    x_data_weekend = df[df.is_weekend][xaxis_col].values[:size]
    y_data_weekend = df[df.is_weekend][yaxis_col].values[:size]

    x_data_workday = df[df.is_weekend.apply(lambda x: not x)][xaxis_col].values[:size]
    y_data_workday = df[df.is_weekend.apply(lambda x: not x)][yaxis_col].values[:size]

    fig = pp.gcf()
    pp.plot(x_data_weekend, y_data_weekend, 'go', label="weekend", alpha=0.1)
    pp.plot(x_data_workday, y_data_workday, 'ro', label="workday", alpha=0.1)

    pp.xlabel(xaxis_col)
    pp.ylabel(yaxis_col)
    pp.legend()
    pp.show()
    fig.savefig("weekends.png", dpi = 400)

def daytimes(df, xaxis_col, yaxis_col, hour_classes=[range(0,6), range(6,8), range(8,13), range(13,16), range(16,19), range(19,21), range(21,24)], size=1000):

    """
    Plots each hour class in a different color
    """
    df_hc = [] #contains df for each hour class
    
    #Set colors
    jet = pp.get_cmap('jet') 
    cNorm  = colors.Normalize(vmin=0, vmax=len(hour_classes))
    scalarMap = cm.ScalarMappable(norm=cNorm, cmap=jet)

    fig = pp.gcf()
    pp.clf()

    for i,hc in enumerate(hour_classes):
        idf = manip.keep_daytimes(df, hours=hc)
        df_hc.append(idf)

        x_data = idf[xaxis_col].values
        y_data = idf[yaxis_col].values

        #select random samples and display them
        perm = np.random.permutation(len(x_data))[:size]
        x_data = [x_data[j] for j in perm]
        y_data = [y_data[j] for j in perm]
        
        pp.plot(x_data, y_data, 'o', label=str(hc), alpha=0.2, color =  scalarMap.to_rgba(i))
        pp.ylim(0, 3000)
        
        
        pp.xlabel(xaxis_col)
        pp.ylabel(yaxis_col)
        pp.legend()



""" ################################### PICKUP TRENDS ############################################# """    

def pickupTrend_Month(df):
    """
    Displays the average number of pickups accross different months.
    """
    _prepFeatures(df)

    fig = pp.gcf()
    pp.clf()

    df.hist(column='month', normed = True, bins = 12)
    pp.xlim(1,13)
    pp.xlabel("Percentage of number of pickups across different months")
    pp.ylabel("Pickups")

    pp.show()

def pickupTrend_DayOfWeek(df):
    """
    Displays the average number of pickups accross different days of the week.
    """
    _prepFeatures(df)

    fig = pp.gcf()
    pp.clf()

    df.hist(column='weekday', normed = True, bins = 7)
    pp.xlim(0,6)
    pp.xlabel("Percentage of number of pickups accross different days of the week (Mon = 0, Sun = 6)")
    pp.ylabel("Pickups")


def pickupTrend_Hour(df):
    """
    Displays the average number of pickups accross different hours.
    """
    _prepFeatures(df)

    fig = pp.gcf()
    pp.clf()

    df.hist(column='hour', normed = True, bins = 24)
    df['hour'].plot(kind='kde', lw = 3)
    pp.xlim(0,23)

    pp.xlabel("Percentage of number of pickups (accross all months) across all times of the day")
    pp.ylabel("Pickups")


def pickupTrend_Hour(df):
    """
    Displays the average number of pickups accross different hours. Separates the plots for each of the day of the week.
    """
    _prepFeatures(df)

    axes = df.hist(column='hour', normed = True, bins = 24, by='weekday') #3x3 array
    for i in range(len(axes)):
        for j in range(len(axes[i])):
            if i==2 and j==1: break
            axes[i][j].set_title(calendar.day_name[int(axes[i][j].get_title())])
            axes[i][j].set_ylabel("Pickups")
            axes[i][j].set_xlabel("Hours")


def _prepFeatures(df):
    """
    Extract additional features (to be displayed in the plot)
    """
    
    #Label weekends in the dataset
    if 'weekday' not in df.columns: df['weekday']    = df.apply(lambda row: row['pick_date'].weekday(), axis=1) 
    if 'is_weekend' not in df.columns: df['is_weekend'] = df.apply(lambda row: row['weekday'] in [5,6], axis=1) 

    if 'month' not in df.columns: df['month'] = df.apply(lambda row: row['pick_date'].month, axis=1) 

    if 'hour' not in df.columns: df['hour'] = df.apply(lambda row: row['pick_date'].hour, axis=1) 
    if 'is_morning' not in df.columns: df['is_morning'] = df.apply(lambda row: row['hour'] in [8, 9, 10, 11, 12, 13], axis=1) 
    if 'is_midday' not in df.columns: df['is_midday'] = df.apply(lambda row: row['hour'] in [14, 15, 16, 17], axis=1) 
    if 'is_evening' not in df.columns: df['is_evening'] = df.apply(lambda row: row['hour'] in [18, 19, 20, 21, 22, 23], axis=1) 
    if 'is_night' not in df.columns: df['is_night'] = df.apply(lambda row: row['hour'] in [0, 1, 2, 3, 4, 5, 6, 7], axis=1) 

def main():
    db = taxiDB.TripQ()

    #Load some random data
    sz = 200000
    df = db.query_Random(sz)

    return df
