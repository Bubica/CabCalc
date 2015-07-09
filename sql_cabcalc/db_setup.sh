#!/bin/bash 

DB_NAME=taxi
TABLE_PREFIX=trip_
WEATHER_TABLE_NAME=weather

TRIP_CSV_DIR=/Users/bubica/Development/CODE/PROJECTS/InsightDataScience2014/Project/data/tripData2013
FARE_CSV_DIR=/Users/bubica/Development/CODE/PROJECTS/InsightDataScience2014/Project/data/fareData2013
WEATHER_CSV_DIR=/Users/bubica/Development/CODE/PROJECTS/InsightDataScience2014/Project/data/weather_2013
PY_DIR=/Users/bubica/Development/CODE/PROJECTS/InsightDataScience2014/Project/code/
PY_MODULE=pycabcalc.app.data_prep.main

DB_DUMP_FOLDER=/Volumes/My_Passport_MAC/InsightDataScience2014/data/mysql_db/taxi_db_web/text_dump

#Command for printing out the size of db
DB_SZ_COMMAND="SELECT table_schema AS DB_Name, Round(Sum(data_length + index_length) / 1024 / 1024, 1) AS DB_Size_in_MB FROM   information_schema.tables  WHERE  table_schema='"$DB_NAME"' GROUP  BY table_schema;"

#Set pythonpath
export PYTHONPATH=$PYTHONPATH:$PY_DIR