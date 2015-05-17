import pandas as pd
import os


def maxCount(fname, hour, dow, month):
    occ = _count("hour", fname, hour = None, dow = dow, month = month)
    
    if not hour:
        return occ['count'].max()
    else:
        return occ[occ.hour==hour]['count'].max()

"""
NOTE: Relative counts proved to be of little interest - the relative counts of pickup and drop off events does not seem to change much
thought out the day (i.e. the busiest points remain the busiest ones regardless of the time of the day, just the absolute number of events
    drops significantly during night hours accross all points)
    
"""
def eventsPerHour(fname, dow = None, month=None):

    """
    For each hub, returns the percentage (%) of traffic that took place in the vicinty of each hub on a particular hour of the day
    (accross the whole year). If the dow argument is provided, the returned traffic information will contain separate records 
    corresponding to the requested day of the week. dow argument is integer value coded in the standard python calendar fashion 
    (i.e. 0==Mon etc). SImilar logic applies to month argument.

    This method is used for animation purposes.
    """    
    return _count("hour", fname, hour = None, dow = dow, month = month)

def eventsPerMonth(fname, dow = None, hour=None):
    return _count("month", fname, hour = hour, dow = dow, month = None)

def eventsPerDay(fname, month = None, hour=None):
    return _count("day", fname, hour = hour, dow = None, month = month)

""" ************************************************************************ """

def _count(gr_attr, fname, hour=None, dow = None, month=None):

    #Load dataset
    occ = pd.read_csv(fname)
    # occ.columns = [u'id', u'lat', u'long', u'x', u'y', u'count', u'hour', u'month', u'day']

    #Retain only the requested day
    if dow:
        occ = occ[occ.day==dow]

    #Retain only the requested month
    if month:
        occ = occ[occ.month==month]

    #Retain only the requested hour of the day
    if hour:
        occ = occ[occ.hour==hour]

    #Group by the hub and the requested attribute (each group will contain data accross all months)
    day_gr = occ.groupby(['hub_id', 'lat', 'long', 'x', 'y', gr_attr])

    #absolute total counts for each hub in each hour on requested day
    occ = day_gr.apply(lambda gr: gr['count'].sum())
    occ.name = 'count'

    #remove multiindex
    occ = occ.reset_index() 

    #compute relative count of pickups/dropoffs (scaled by the total number of events accross all hubs in instance of gr_attr)
    occ_rel = occ.groupby(gr_attr).apply(lambda x: x['count']/x['count'].sum())
    occ_rel.name = 'count'
    occ['count_rel'] = occ_rel.swaplevel(1,0).reset_index(level=1)['count']

    return occ


def test():
    out_folder = os.path.dirname(os.path.abspath(__file__)) #dir of this module
    fname_default = out_folder+"/hub_occupancy_pickup.csv"
    return relativePerHour(fname=fname_default)



