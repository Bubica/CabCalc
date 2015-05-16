import math
import MySQLdb as mdb
import sys
import pandas as pd
import numpy as np


class DBHandler(object):

    """
    Maintains the connection towards the database and executes given queries and commands
    """
    
    def __init__(self, **kwargs):
        self.connection = self._connect2Db(**kwargs) 

    def _connect2Db(self, host = 'localhost' ,user = 'root', passwrd = '', dbName = 'taxi'):

        #Estabilshes the connection to the database
        connection=None
        try:
            connection = mdb.connect(host, user, passwrd, dbName);
            print "Connect", connection
            cur = connection.cursor()
            cur.execute("SELECT VERSION()")
        
            ver = cur.fetchone()
            
            print "Database version : %s " % ver
            
        except mdb.Error, e:
          
            print "Error %d: %s" % (e.args[0],e.args[1])  
                
            if connection:    
                connection.close()
                connection = None
                
        return connection

    def selectQuery(self, sqlQuery):
        
        """ Executes SELECT query and returns the result in DataFrame format """
        cur = self.connection.cursor(mdb.cursors.DictCursor)
        cur.execute(sqlQuery)
        rows = cur.fetchall()
        
        return pd.DataFrame(list(rows))

    def count(self, sqlQuery):
        
        """ Runs count query and returns integer result """

        cnt = self.selectQuery(sqlQuery).ix[0].values[0]
        return cnt

    def modify(self, cmd, args = None, commit = True):
        """
        Changes the table (updates, adds etc) and does not return the value.
        If multiple modifications will be made, invoke commit only once in a while
        """
        cur = self.connection.cursor(mdb.cursors.DictCursor)

        if not args:
            ret = cur.execute(cmd)
        else:
            ret = cur.execute(cmd, args)

        if commit:
            self.connection.commit() 


#String condition of column (float) not being 0
# colNotZero = lambda col_name: col_name+">0 OR "+col_name+"<0"
    