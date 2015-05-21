import pandas as pd
import numpy as np
import datetime
import calendar
import sys
import localDbHandler
import time
import math
from ..geo import tools as geotools


"""
Script for handling taxi related queries in local mysql database. 
Some filtering is done on the db level, some filtering (e.g. based on the day of the week)
is done in python pandas object.
"""


class Q(object):

    force_index = "ind_combo" #forces this index when performing search (query_Routes only for now)

    """
    A generic query class.
    """
    def __init__(self, handlerType=None):
        self._setDbConnection(handlerType)

    def _setDbConnection(self, handlerType):
        if handlerType==None:
            handlerType = localDbHandler

        self.dbHandler = handlerType.DBHandler(dbName = "taxi")

    def getDbHandler(self):
        return self.dbHandler

    def _fetchData(self, q):

        """ RunsSQL query and retrieves the data from the database """
        print "Query:"    
        print q
        print

        ts = time.time()
        df = self.dbHandler.selectQuery(q)
        te = time.time() 
        qtime = (te-ts)

        print "Query time (sec): ", qtime,
        print "; Records found: ", len(df)

        return df, qtime   

        

class WeatherQ(Q):

    """
    Class that performs weather related queries in the database.
    """

    def query_All(self, cols='All', limit = None):
        """
        Returns weather data.
        """
        table = 'weather'

        if cols =='All':
            col_str = "*"
        else:
            col_str = ",".join(cols) #concatenate column names in one big string separated with commas
            
        q = "SELECT %s FROM %s " % (col_str, table)

        if limit is not None:
            q = q +" LIMIT "+str(limit)

        df, qtime = self._fetchData(q)
        print "Total query time", qtime

        return df
        
    def query_Month(self, month, cols = 'All',dof_pick=None, limit=None):
        """
        Returns weather data for the particular month in 2013.
        """
        table = 'weather'

        if cols =='All':
            col_str = "*"
        else:
            col_str = ",".join(cols) #concatenate column names in one big string separated with commas
            
        q = "SELECT %s FROM %s " % (col_str, table)
        q += " WHERE MONTH(time) = "+ str(month)
        if dof_pick is not None:
            sqlDOF = 1+((dof_pick + 1)%7) #python dof differs from myql
            q += " AND DAYOFWEEK(time) = "+str(sqlDOF)

        if limit is not None:
            q = q +" LIMIT "+str(limit)

        df, qtime = self._fetchData(q)
        print "Total query time", qtime

        return df


class TripQ(Q):

    getTripTbl = lambda self, month: "trip_"+str(month) #given the month, return the table containing the data for this month


    """
    Class that performs trip related queries in the database.
    """
    def query_Month(self, month, cols = 'All', dof_pick=None, limit=None):
        """
        Returns requested columns for a given month.
        dof_pick: day of the week for pick_date column (0==Monday, 1==Tuesday etc)
        cols: list of columns to be returned
        """

        trip_table = self.getTripTbl(month)

        if cols =='All':
            col_str = "*"
        else:
            col_str = ",".join(cols) #concatenate column names in one big string separated with commas
            
        q = "SELECT %s FROM %s " % (col_str, trip_table)

        if dof_pick is not None:
            sqlDOF = 1+((dof_pick + 1)%7) #python dof differs from myql
            q += " WHERE DAYOFWEEK(pick_date) = "+str(sqlDOF)

        if limit is not None:
            q = q +" LIMIT "+str(limit)

        df, qtime = self._fetchData(q)
        print "Total query time", qtime

        return df

    def query_Month_Piecewise(self, month, cols = 'All', chunkSz = 200000):

        """ 
        Loads the data from the db in pieces.
        The trip table requires a integer column named "ord_no" with unique value per record.
        """

        trip_table = self.getTripTbl(month)
        
        tblSz = self.dbHandler.count("SELECT MAX(ord_no) FROM "+trip_table) #use ord_no max rather than count since Max(ord_no)>= count(*) -- some records may be deleted previously
        dbChunks = int(math.ceil(tblSz/(1.*chunkSz)))

        if cols =='All':
                col_str = "*"
        else:
                col_str = ",".join(cols) #concatenate column names in one big string separated with commas
                
        sqlPattern = "SELECT %s FROM %s WHERE ord_no BETWEEN %d AND %d "

        for chunk in range(dbChunks):

            #compute start and end index of this chunk
            si = chunk*chunkSz
            ei = (chunk+1)*chunkSz-1

            sqlQuery = sqlPattern % (col_str, trip_table, si, ei)

            df = self.dbHandler.selectQuery(sqlQuery)

            yield df

    def count_Records(self, month):
        
        """ Returns number of records for the given month """

        trip_table = self.getTripTbl(month)
        q = """SELECT COUNT(*) FROM %s""" % (trip_table)
        cnt = self.dbHandler.count(q)

        return cnt

    def count_Routes(self, s_point_lonlat, e_point_lonlat, env_sz):
        """
        Provides a count of routes accross all months.
        NOTE: some c/p from query_Routes - TODO clean this up
        """
        s_point = geotools.sphericalConversion(*s_point_lonlat)
        e_point = geotools.sphericalConversion(*e_point_lonlat)

        #Define rectangle around the start point
        s_env_minx = s_point[0]-env_sz/2.
        s_env_maxx = s_point[0]+env_sz/2.
        s_env_miny = s_point[1]-env_sz/2.
        s_env_maxy = s_point[1]+env_sz/2.
        
        #Define rectangle around the start point
        e_env_minx = e_point[0]-env_sz/2.
        e_env_maxx = e_point[0]+env_sz/2.
        e_env_miny = e_point[1]-env_sz/2.
        e_env_maxy = e_point[1]+env_sz/2.

        month_cnt = {}
        for i in range(1,13):
            tblName = self.getTripTbl(i)
            
            q = "SELECT COUNT(*) FROM " + tblName
            q = q + " WHERE "
            q = q + ("pick_x BETWEEN %f AND %f AND pick_y BETWEEN %f AND %f AND " % (s_env_minx, s_env_maxx, s_env_miny, s_env_maxy))
            q = q + ("drop_x BETWEEN %f AND %f AND drop_y BETWEEN %f AND %f" % (e_env_minx, e_env_maxx, e_env_miny, e_env_maxy))

            cnt = self.dbHandler.selectQuery(q)
            month_cnt[i] = cnt

        return month_cnt

    def query_Routes(self, s_point_lonlat, e_point_lonlat, env_sz, date_span = None, limit=None, random=False, cols=None):
        """
        Find all routes in the database that start in the rectangle neighbourhood of the start point and terminate in the
        neighbourhood of the end point.
        env_sz: size of the neighbouring area where to search for the points
        """
        
        s_point = geotools.sphericalConversion(*s_point_lonlat)
        e_point = geotools.sphericalConversion(*e_point_lonlat)

        #Define rectangle around the start point
        s_env_minx = s_point[0]-env_sz/2.
        s_env_maxx = s_point[0]+env_sz/2.
        s_env_miny = s_point[1]-env_sz/2.
        s_env_maxy = s_point[1]+env_sz/2.
        
        #Define rectangle around the start point
        e_env_minx = e_point[0]-env_sz/2.
        e_env_maxx = e_point[0]+env_sz/2.
        e_env_miny = e_point[1]-env_sz/2.
        e_env_maxy = e_point[1]+env_sz/2.
        
        if date_span==None: #search all tables
            t1 = datetime.datetime(2013, 1, 1, 0, 0, 0)
            t2 = datetime.datetime(2013, 12, 31, 23, 59, 59) 
            date_span = (t1, t2)

        if limit is not None:
            #since a single Route query may result in several requests to the db (to the different tables), 
            #limit value needs to be split so that total number of retrieved records matches requested number
            td = (date_span[1] - date_span[0]).days +1 #number of days in the interval
            rand_days = [date_span[0] + datetime.timedelta(i) for i in np.random.randint(0, td, limit)] #sample random dates from the interval
            smpl_per_month = np.bincount([i.month for i in rand_days]) #retain months only and count how many of samples was sampled in each month

        searchTbls = self._tableTimeRange(date_span[0], date_span[1])
        df = pd.DataFrame([]) #resulting dataframe
        qtime = 0 #time profiling

        if not cols:
            cols = "*" #columns to return - return all
        else:
            cols = ','.join(cols)

        for m in searchTbls.keys():
            
            table, rng = searchTbls[m]

            q = "SELECT %s FROM %s AS trip " % (cols, table)  

            if self.force_index:
                q += " FORCE INDEX ({0}) ".format(self.force_index)

            #Where conditions
            q = q + " WHERE "
            q = q + ("pick_x BETWEEN %f AND %f AND pick_y BETWEEN %f AND %f AND " % (s_env_minx, s_env_maxx, s_env_miny, s_env_maxy))
            q = q + ("drop_x BETWEEN %f AND %f AND drop_y BETWEEN %f AND %f" % (e_env_minx, e_env_maxx, e_env_miny, e_env_maxy))

            if rng is not None: 

                #only a subset of entries needed - depending on the time
                t1 = rng[0]; t2 = rng[1]
                qp=""
                

                if t1 is not None:
                    qp = qp + " DAY(pick_date) >= '" + str(t1.day) + "'"
                    # qd = qd + " DAY(drop_date) >= '" + str(t1.day) + "'"
                    if t2 is not None:
                        qp = qp + " AND "
                        # qd = qd + " AND "

                if t2 is not None:
                    qp = qp + " DAY(pick_date) <= '" + str(t2.day) +"'"
                    # qd = qd + " DAY(drop_date) <= '" + str(t2.day) +"'"
                q = q + " AND " + qp 
                #q = q +" AND " + qd

            if random: #SLOW! This is used when return random subset of routes from the db
                q = q + "ORDER BY RAND()"

            if limit is not None:
                smpl = smpl_per_month[m]
                print "LIMIT"
                q = q +" LIMIT "+str(smpl)
        
            dfq, qt = self._fetchData(q)
            df = pd.concat([df, dfq], axis = 0)
            qtime += qt

        print "Total query time", qtime
        return df


    def _tableTimeRange(self, t_start, t_end):

        """
        Returns the information where the data is stored based on the given time interval.
        Each returned tuple containes the name of the table and the range of the data in the table that falls within the interval.
        If the range is not set (i.e. is None), then the all records in that table fall in the given range.

        Example:

        Output:
        {4: ('trip_4', (datetime.datetime(2015, 4, 16, 17, 44), None)),
        5: ('trip_5', None),
        6: ('trip_6', None),
        7: ('trip_7', None),
        8: ('trip_8', (None, datetime.datetime(2015, 8, 12, 17, 44)))}
        """

        tbls = {}
        year = 2013
        m_start = t_start.month
        d_start = t_start.day
        h_start = t_start.hour
        mi_start = t_start.minute
        s_start = t_start.second

        m_end = t_end.month
        d_end = t_end.day
        h_end = t_end.hour
        mi_end = t_end.minute
        s_end = t_end.second

        for i in xrange(m_start, m_end+1):
            tbl = self.getTripTbl(i)

            rng = None #range of dates to search in this table, set to None when the whole table is searched

            t1 = None; t2 = None

            if i==m_start and not (d_start == 1 and h_start == 0 and mi_start == 0 and s_start == 0):
                t1 = t_start
                rng = (t1, t2)

            if i==m_end and not (d_end == calendar.monthrange(year, m_end)[1] and h_end == 23 and mi_end == 59 and s_end == 59):
                t2 = t_end
                rng = (t1, t2)

            tbls[i] = (tbl, rng)

        return tbls

    def query_Random(self, num, date_span = None, cols = None):
        """
        Returns num random samples from trip database.
        months: month range used to sample samples from
        """

        #columns to return
        if not cols:
            cols = "*" #columns to return - return all
        else:
            cols = ','.join(cols)

        if date_span==None: #search all tables
            t1 = datetime.datetime(2013, 1, 1, 0, 0, 0)
            t2 = datetime.datetime(2013, 12, 31, 23, 59, 59) 
            date_span = (t1, t2)

        td = (date_span[1] - date_span[0]).days +1 #number of days in the interval

        #random assingment of samples to different trip tables
        rand_days = [date_span[0] + datetime.timedelta(i) for i in np.random.randint(0, td, num)] #random day instances from the interval
        smpl_per_month = np.bincount([i.month for i in rand_days]) #retain months only and count how many of each
        table_time_rng = self._tableTimeRange(date_span[0], date_span[1])#range of each trip table

        df = pd.DataFrame([]) #resulting dataframe
        qtime = 0

        for m in range(date_span[0].month, date_span[1].month+1):

            if m >= len(smpl_per_month): 
                break

            smpl_cnt = smpl_per_month[m]
            if smpl_cnt <=0: continue

            table = self.getTripTbl(m)
            rng = table_time_rng[m][1]

            q = "SELECT %s FROM %s AS trip" % (cols, table)

            if rng is not None: 

                #only a subset of entries needed - depending on the time
                t1 = rng[0]
                t2 = rng[1]
                qp = ""

                print type(t1)
                if t1 is not None:
                    qp = qp + " DAY(pick_date) >= " + str(t1.day)
                    if t2 is not None:
                        qp = qp + " AND "
                    
                if t2 is not None:
                    qp = qp + " DAY(pick_date) <= " + str(t2.day)

                q = q +" WHERE " + qp   

            q = q + " ORDER BY RAND() LIMIT "+str(smpl_cnt) #slow, takes about 1 min per table - only for debugging

            dfq, qt = self._fetchData(q)
            qtime += qt
            
            df = pd.concat([df, dfq], axis = 0)

        print "Total query time (sec): ", qtime
        return df


    def query_NeighbourPoints(self, point_lonlat, env_sz, pick=True, drop=False, date_span = None):
        """
        Given a single point in long/lat coordinates, return all points in the neighbourhood of this point.
        Used for display/debugging purpose only.
        """
        
        point = geotools.sphericalConversion(*point_lonlat)
        
        #Define rectangle around the point
        env_minx = point[0]-env_sz/2.
        env_maxx = point[0]+env_sz/2.
        env_miny = point[1]-env_sz/2.
        env_maxy = point[1]+env_sz/2.
        
        if date_span==None: #search all tables
            t1 = datetime.datetime(2013, 1, 1, 0, 0, 0)
            t2 = datetime.datetime(2013, 12, 31, 23, 59, 59) 
            date_span = (t1, t2)

        trip_tbls = self._tableTimeRange(date_span[0], date_span[1]).values()

        df = pd.DataFrame([])

        for table, rng in trip_tbls:

            q = "SELECT * FROM %s WHERE " % (table)
            if pick:
                q = q + ("pick_x BETWEEN %f AND %f AND pick_y BETWEEN %f AND %f" % (env_minx, env_maxx, env_miny, env_maxy))
                if drop:
                    q = q +" AND "
            if drop:
                q = q + ("drop_x BETWEEN %f AND %f AND drop_y BETWEEN %f AND %f" % (env_minx, env_maxx, env_miny, env_maxy))

            if rng is not None: 

                #only a subset of entries needed - depending on the time
                t1 = rng[0]; t2 = rng[1]
                qp=""

                if t1 is not None:
                    qp = qp + " pick_date >= " + str(t1)
                    if t2 is not None:
                        qp = qp + " AND "
                    
                if t2 is not None:
                    qp = qp + " pick_date <= " + str(t2)

                q = q +" AND " + qp         

            dfq, _ = self._fetchData(q)
            df = pd.concat([df, dfq], axis = 0)

        return df

    def push2Db(self, month, df, match_column = 'ord_no', store_columns=['err_flag']):
            
        """
        Propagates changes to the database - simply replaces existing table with the values in the dataframe.
        match_column : column on which match between local dataframe and mysql table is performed
        store_columns: data to be pushed to the db is contained in these columns

        NOTE: the columns of the given dataframe that we are pushing to the db need to match in their name 
        with the columns in the db table
        """
        trip_table = self.getTripTbl(month)

        #Dump to the database - record by record (not the most elegant solution but it's only done once)
        #Compose the command template

        cmd = "UPDATE " + trip_table + " SET "
        for ic,c in enumerate(store_columns):
            cmd += c + "=%s"
            if ic< len(store_columns)-1:
                cmd += ", "

        cmd += " WHERE ord_no=%s"        

        for i in df.iterrows(): #i == tuple (index, Series)
            vals = [i[1][c] for c in store_columns]
            vals.append(int(i[1]['ord_no']))
            vals = tuple(vals)

            commit = False
            if i[0] % 1000: commit = True

            # print "Generic cmd:", cmd, "vals: ", vals
            self.dbHandler.modify(cmd, vals, commit = commit)
     
