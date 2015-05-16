import pandas.io.gbq as gbq
from subprocess import call

taxi_table = '833682135931:nyctaxi.trip_data' #just for back-up


class DBHandler(object):

    def __init__(self, *kwargs):
        #Init bq
        call(["bq", "init"])

    def selectQuery(self, sqlQuery):

        #Retrieve query
        df = gbq.read_gbq(sqlQuery, project_id='buba-mala')
        return df