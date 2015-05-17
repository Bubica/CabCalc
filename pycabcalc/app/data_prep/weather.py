import math
from ..db import taxiDB 

"""
Module for insering values in the column which indicates the presence or precipitation for the given record (rain or snow).
"""

def mark(month):

    chunk_sz = 20000
    trip_handler = taxiDB.TripQ()
    weather_handler = taxiDB.WeatherQ()

    chunk_iter = trip_handler.query_Month_Piecewise(month, chunkSz=chunk_sz)
    weather_data = weather_handler.query_Month(month, cols = 'All').sort('time')

    #Helper function to match trip and weather records

    def _time_match(trip_date):
        i = weather_data.time.searchsorted(trip_date)[0]
        if i == len(weather_data): i -=1 #trip_data > all records in weather

        w_rec = weather_data.iloc[i] #weather record that matches trip record in time

        return w_rec['precip_float'], w_rec['precip_bool'] 

    cnt = 0
    #Performing the operation on the chunk of data - to push the interim results to the db right after they have finished
    for trip_data in chunk_iter:

        #NOTE: trip_data.pick_date.map(_time_match) will return series with tuple values
        
        print "Next chunk, month: ", month, " Count:", cnt
        cnt +=1

        trip_data['precip_f'], trip_data['precip_b'] = zip(*trip_data.pick_date.map(_time_match))

        # _checkManhattanBox(df)
        # _updateErrFlag(df)
        # _deleteTempColumns(df)

        trip_handler.push2Db(month, trip_data, match_column = 'ord_no', store_columns=['precip_f', 'precip_b'])





