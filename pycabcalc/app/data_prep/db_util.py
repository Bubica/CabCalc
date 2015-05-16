from ..db import taxiDB 
from ..db.localDbHandler import DBHandler

dbHandler = DBHandler()


"""
Module facilitates composing relevant queries for needed for data cleaning.
"""

def tblSz(month):

    global dbHandler
    
    tblName = taxiDB.getTripTbl(month) 
    sqlQuery = """SELECT COUNT(*) FROM %s""" % (tblName)
    cnt = dbHandler.count(sqlQuery)

    return cnt

def load(month, start, end):

    """ Loads the data from the db (starting with 'start' ord no and ending with 'end' """

    global dbHandler

    tblName = taxiDB.getTripTbl(month) 
    sqlQuery = """SELECT %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s FROM %s""" % ('ord_no', 'pick_lon', 'pick_lat', 'drop_lon', 'drop_lat', 'pick_x', 'drop_x', 'pick_y', 'drop_y', 'trip_distance', 'err_flag', tblName)
    sqlQuery += """ WHERE ord_no BETWEEN %d AND %d """ % (start, end)
    print sqlQuery
    df = dbHandler.selectQuery(sqlQuery)

    return df

def push2Db(month, df, columns=['err_flag']):
        
    """
    Propagates changes to the database - simply replaces existing table with the values in the dataframe.
    """
    tblName = taxiDB.getTripTbl(month) 

    # #Add the new column (manhattan one is NOT propagated to db)
    # cmd = "ALTER TABLE " + tblName +" ADD COLUMN shortest_route FLOAT"
    # dbHandler.modify(cmd)

    #Dump to the database - record by record (not the most elegant solution but it's only done once)
    #Compose the command template

    cmd = "UPDATE " + tblName + " SET "
    for ic,c in enumerate(columns):
        cmd += c + "=%s"
        if ic< len(columns)-1:
            cmd += ", "

    cmd += " WHERE ord_no=%s"        

    for i in df.iterrows(): #i == tuple (index, Series)
        vals = [i[1][c] for c in columns]
        vals.append(int(i[1]['ord_no']))
        vals = tuple(vals)

        commit = False
        if i[0] % 1000: commit = True

        # print "Generic cmd:", cmd, "vals: ", vals
        dbHandler.modify(cmd, vals, commit = commit)