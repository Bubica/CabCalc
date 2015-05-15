#!/bin/bash 

#Removes obsolete columns from each table in the database

TRIP_CSV_DIR=/Users/bubica/Development/CODE/InsightDataScience2014/Project/data/tripData2013/v3
FARE_CSV_DIR=/Users/bubica/Development/CODE/InsightDataScience2014/Project/data/fareData2013

DB_NAME=taxi
TABLE_PREFIX=trip_


for TABLE_ID in `seq 1 12`;
do
	TABLE_NAME=$TABLE_PREFIX$TABLE_ID

	# echo "Deleting erroneous records"
	# SQL_COMMAND="DELETE FROM "$TABLE_NAME" WHERE err_flag=1"
	# mysql -e "$SQL_COMMAND" -u root $DB_NAME

	#Obtain names of all columns in this table
	column_cmd="SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='$DB_NAME' AND TABLE_NAME='$TABLE_NAME'"
	cols=`mysql -s -N -e "$column_cmd" -u root`
	
	col_list=(${cols// / })
	echo $col_list

	# echo "Reclaim free space"
	# SQL_CMD="OPTIMIZE TABLE "$TABLE_NAME
	# mysql -e "$SQL_CMD" -u root  $DB_NAME

done



