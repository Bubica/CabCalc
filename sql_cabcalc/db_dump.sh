#!/bin/bash

#Dump/Load taxi database into/from local text file - backup purpose

#Load the basic setup
source db_setup.sh

opt=$1

if [ "$opt" = "store" ]; then 
	echo "Storing the database into txt files"
	#csv files located in /usr/local/mysql/data/taxi

	for i in {1..12}
	do
		echo "Dumping month $i" 
		TABLE_NAME=$TABLE_PREFIX$i
		SQL_CMD="SELECT * INTO OUTFILE '"$TABLE_NAME"_dump.csv' FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '\"' LINES TERMINATED BY '\n' FROM $TABLE_NAME"
		mysql -e "$SQL_CMD" -u root  $DB_NAME

	done
	
elif [ "$opt" = "load_full" ]; then

	#the complete db in the file (not partial version suited for the web)

	DB_DUMP_FOLDER=/Volumes/My_Passport_MAC/InsightDataScience2014/data/mysql_db/taxi_db_full_2/text_dump_all_columns
	echo "    Loading the database from txt files in $DB_DUMP_FOLDER"

	echo "Creating the database $DB_NAME"
	SQL_CMD="CREATE DATABASE IF NOT EXISTS "$DB_NAME
	mysql -e "$SQL_CMD" -u root 

	SQL_CMD="SET GLOBAL innodb_file_per_table=1"
	mysql -e "$SQL_CMD" -u root 

	for i in {1..12}
	do
		TABLE_NAME=$TABLE_PREFIX$i
		
		echo "Loading "$TABLE_NAME

		SQL_CMD="CREATE TABLE IF NOT EXISTS $TABLE_NAME (pick_date DATETIME, trip_time_in_secs SMALLINT, trip_distance FLOAT, pick_x FLOAT, pick_y FLOAT, drop_x FLOAT, drop_y FLOAT, err_flag TINYINT(1), total_wo_tip FLOAT, pick_lon DOUBLE, pick_lat DOUBLE, drop_lon DOUBLE, drop_lat DOUBLE, ord_no INT, precip_f FLOAT, precip_b TINYINT(1), manhattan TINYINT(1))"
		mysql -e "$SQL_CMD" -u root  $DB_NAME

		SQL_CMD="LOAD DATA LOCAL INFILE '"$DB_DUMP_FOLDER"/"$TABLE_NAME"_dump.csv' IGNORE INTO TABLE $TABLE_NAME FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '\"' LINES TERMINATED BY '\n' (pick_date, trip_time_in_secs, trip_distance, pick_x, pick_y, drop_x, drop_y, err_flag, total_wo_tip, pick_lon, pick_lat, drop_lon, drop_lat, ord_no, precip_f, precip_b, manhattan)"
		mysql -e "$SQL_CMD" -u root  $DB_NAME
	done

elif [ "$opt" = "load_web" ]; then

	DB_DUMP_FOLDER=/Volumes/My_Passport_MAC/InsightDataScience2014/data/mysql_db/taxi_db_web/text_dump
	echo "    Loading the database from txt files in $DB_DUMP_FOLDER"
	#the partial db suited for the web

	echo "Creating the database $DB_NAME (web option)"
	SQL_CMD="CREATE DATABASE IF NOT EXISTS "$DB_NAME
	
	mysql -e "$SQL_CMD" -u root 

	SQL_CMD="SET GLOBAL innodb_file_per_table=1"
	mysql -e "$SQL_CMD" -u root 

	for i in {1..12}
	do
		TABLE_NAME=$TABLE_PREFIX$i

		echo "Loading "$TABLE_NAME

		SQL_CMD="CREATE TABLE IF NOT EXISTS $TABLE_NAME (pick_date DATETIME, trip_time_in_secs SMALLINT, trip_distance FLOAT, pick_x FLOAT, pick_y FLOAT, drop_x FLOAT, drop_y FLOAT, total_wo_tip FLOAT, precip_f FLOAT)"
		mysql -e "$SQL_CMD" -u root  $DB_NAME

		#NOTE: ON AWS Ubuntu AMI instance replace: "LOAD DATA LOCAL INFILE" --> "LOAD DATA INFILE"
		SQL_CMD="LOAD DATA LOCAL INFILE '$DB_DUMP_FOLDER/"$TABLE_NAME"_dump.csv' IGNORE INTO TABLE $TABLE_NAME FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '\"' LINES TERMINATED BY '\n' (pick_date, trip_time_in_secs, trip_distance, pick_x, pick_y, drop_x, drop_y, total_wo_tip, precip_f)"
		echo $SQL_CMD
		# mysql -e "$SQL_CMD" -u root  $DB_NAME

		# following is an attempt to replace DATETIME (8 bytes) with TINYINT and SMALLINT (3 bytes in total) - reduction cca 50 MB per table -- not worth it

		# SQL_CMD="CREATE TABLE IF NOT EXISTS $TABLE_NAME (day TINYINT UNSIGNED, mins_since_midnight SMALLINT UNSIGNED, trip_time_in_secs SMALLINT, trip_distance FLOAT, pick_x FLOAT, pick_y FLOAT, drop_x FLOAT, drop_y FLOAT, total_wo_tip FLOAT, precip_f FLOAT)"
		# mysql -e "$SQL_CMD" -u root  $DB_NAME

		# SQL_CMD="LOAD DATA LOCAL INFILE '"$DB_DUMP_FOLDER"/trip_1_dump.csv' IGNORE INTO TABLE $TABLE_NAME 
		# 	FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '\"' LINES TERMINATED BY '\n' 
		# 	(@pick_date, trip_time_in_secs, trip_distance, pick_x, pick_y, drop_x, drop_y, total_wo_tip, precip_f)
		# 	SET 
		# 	day := DAY(@pick_date),
		# 	mins_since_midnight := HOUR(@pick_date)*60+MINUTE(@pick_date)"

		mysql -e "$SQL_CMD" -u root  $DB_NAME

	done


else
	echo "    Unrecognized option"
fi




