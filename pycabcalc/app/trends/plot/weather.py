from ...db import taxiDB
from matplotlib import pyplot as pp

def precip_values():
    db = taxiDB.WeatherQ()
    df = db.query_All()

    #Distribution of precipitation values when raining
    df[df.precip_bool==1].hist(column = 'precip_float', bins = 50)