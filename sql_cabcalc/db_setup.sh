#!/bin/bash 

DB_NAME=taxi
TABLE_PREFIX=trip_

TRIP_CSV_DIR=/Users/bubica/Development/CODE/PROJECTS/InsightDataScience2014/Project/data/tripData2013
FARE_CSV_DIR=/Users/bubica/Development/CODE/PROJECTS/InsightDataScience2014/Project/data/fareData2013
WEATHER_CSV_DIR=/Users/bubica/Development/CODE/PROJECTS/InsightDataScience2014/Project/data/weather_2013
PY_DIR=/Users/bubica/Development/CODE/PROJECTS/InsightDataScience2014/Project/code/python/
PY_MODULE=taxi.data_prep.main

DB_DUMP_FOLDER=/Volumes/My_Passport_MAC/InsightDataScience2014/data/mysql_db/taxi_db_new
DB_SZ_COMMAND="SELECT * FROM (SELECT table_schema \"DBName\",     Round(Sum(data_length + index_length) / 1024 / 1024, 1) \"DB Size in MB\"  FROM   information_schema.tables  GROUP  BY table_schema) AS total WHERE DBName=\""$DB_NAME"\""