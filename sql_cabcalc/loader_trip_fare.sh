#!/bin/bash 

#Load the basic setup
source db_setup.sh

#Prefixes of temp tables
TRIP_TABLE_PREFIX=trip_tmp_
FARE_TABLE_PREFIX=fare_tmp_


echo "Creating the database $DB_NAME"
SQL_CMD="CREATE DATABASE "$DB_NAME
mysql -e "$SQL_CMD" -u root 

#Select file_per_table option to enable reclaiming space following initial filtering
SQL_CMD="SET GLOBAL innodb_file_per_table=1"
mysql -e "$SQL_CMD" -u root 

#Set pythonpath
export PYTHONPATH=$PY_DIR

#Filter thresholds
TH_TRIP_TIME_LOW=60 #at least 1 min long trip
TH_TRIP_TIME_UP=4320 #at most 1.2 hours long trip (threshold selected using histogram of raw data)
TH_TRIP_DIST_LOW=0.3 #at least half a kilometre long trip
TH_TRIP_DIST_UP=15 #(threshold selected using histogram of raw data)
TH_LON_LOW=-74.03 #Manhattan bounding box (not tight!)
TH_LON_UP=-72.99
TH_LAT_LOW=40.68
TH_LAT_UP=40.9 	
TH_SPEED=30 #Allowed NYC speed limit
TH_PASSANGER=1 #records with more than one passanger may have a detour - discard those
TH_EUCL_DIST_LOW=0.25 #from the histogram of the sample of data
TH_EUCL_DIST_UP=1.0

t_start=$(date)
for trip_f in $TRIP_CSV_DIR/trip_data*.csv
do

	t_start_a=$(date)

	#split name of the file to create the table of corresponding name
	SPLIT=(${trip_f//_/ })
	TMP=${SPLIT[2]}
	
	SPLIT=(${TMP//./ })
	TABLE_ID=${SPLIT[0]}
	TRIP_TABLE_NAME="$TRIP_TABLE_PREFIX$TABLE_ID"
	FARE_TABLE_NAME="$FARE_TABLE_PREFIX$TABLE_ID"
	FINAL_TABLE_NAME="$TABLE_PREFIX$TABLE_ID"
	fare_f="$FARE_CSV_DIR/trip_fare_$TABLE_ID.csv" 

	echo "Table index: $TABLE_ID"
	echo "Input trip file: $trip_f"
	echo "Input fare file: $fare_f"
	echo "Creating table: $TRIP_TABLE_NAME"

	#Check if the final table exists - if so, skip this table and proceed
	SQL_CMD="SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = '"$DB_NAME"' AND table_name = '"$FINAL_TABLE_NAME"'"
	exists=`mysql -s -N -e "$SQL_CMD" -u root  $DB_NAME`

	if [ $exists -eq 1 ]
	then 
		echo "    ****   Final table already in the database - skipping!"
		continue	
	fi

	#Create a new trip table and populate it with data from the file
	SQL_CMD="CREATE TABLE IF NOT EXISTS "$TRIP_TABLE_NAME" (medallion CHAR(35) NOT NULL, pick_date DATETIME NOT NULL, drop_date DATETIME NOT NULL, 
	trip_time_in_secs SMALLINT NOT NULL, trip_distance FLOAT NOT NULL, pick_lon DOUBLE NOT NULL, pick_lat DOUBLE NOT NULL, drop_lon DOUBLE NOT NULL, 
	drop_lat DOUBLE NOT NULL, pick_x FLOAT NOT NULL, pick_y FLOAT NOT NULL, drop_x FLOAT NOT NULL, drop_y FLOAT NOT NULL, 
	err_flag TINYINT(1) NOT NULL DEFAULT 0, ord_no INT NOT NULL AUTO_INCREMENT, PRIMARY KEY (ord_no))"

	mysql -e "$SQL_CMD" -u root  $DB_NAME

	echo "Loading data into $TRIP_TABLE_NAME"

	SQL_CMD="LOAD DATA LOCAL INFILE '"$trip_f"' IGNORE INTO TABLE "$TRIP_TABLE_NAME" FIELDS TERMINATED BY ',' 
	LINES TERMINATED BY '\n' IGNORE 1 LINES (medallion, @hack_license, @vendor_id, @rate_code, @store_and_fwd_flag, 
	pick_date, drop_date, @passenger_count, trip_time_in_secs, trip_distance, pick_lon, pick_lat, 
	drop_lon, drop_lat) 
	SET
	err_flag := IF(trip_distance/trip_time_in_secs * 3600 >"$TH_SPEED" OR @passenger_count>"$TH_PASSANGER" OR trip_distance<"$TH_TRIP_DIST_LOW" OR trip_distance>"$TH_TRIP_DIST_UP" OR trip_time_in_secs<"$TH_TRIP_TIME_LOW" OR trip_time_in_secs>"$TH_TRIP_TIME_UP" OR pick_lat<"$TH_LAT_LOW" OR pick_lat>"$TH_LAT_UP" OR drop_lat<"$TH_LAT_LOW" OR drop_lat>"$TH_LAT_UP", 1,0),
	pick_x:=3959 * COS(RADIANS(pick_lat)) * COS(RADIANS(pick_lon)), 
	pick_y:=3959 * COS(RADIANS(pick_lat)) * SIN(RADIANS(pick_lon)), 
	drop_x:=3959 * COS(RADIANS(drop_lat)) * COS(RADIANS(drop_lon)), 
	drop_y:=3959 * COS(RADIANS(drop_lat)) * SIN(RADIANS(drop_lon))"

	# If dropping non Manhattan routes:
	# err_flag := IF(trip_distance/trip_time_in_secs * 3600 >"$TH_SPEED" OR @passenger_count>"$TH_PASSANGER" OR trip_distance<"$TH_TRIP_DIST_LOW" OR trip_distance>"$TH_TRIP_DIST_UP" OR trip_time_in_secs<"$TH_TRIP_TIME_LOW" OR trip_time_in_secs>"$TH_TRIP_TIME_UP" OR pick_lon<"$TH_LON_LOW" OR pick_lon>"$TH_LON_UP" OR drop_lon<"$TH_LON_LOW" OR drop_lon>"$TH_LON_UP" OR pick_lat<"$TH_LAT_LOW" OR pick_lat>"$TH_LAT_UP" OR drop_lat<"$TH_LAT_LOW" OR drop_lat>"$TH_LAT_UP", 1,0),
	mysql -e "$SQL_CMD" -u root  $DB_NAME

	echo "Creating table $FARE_TABLE_NAME"
	SQL_CMD="CREATE TABLE IF NOT EXISTS "$FARE_TABLE_NAME" (medallion CHAR(35) NOT NULL, 
	pick_date DATETIME NOT NULL, fare_amount FLOAT NOT NULL, surcharge FLOAT NOT NULL, 
	mta_tax FLOAT NOT NULL, tip_amount FLOAT NOT NULL, tolls_amount FLOAT NOT NULL, 
	total_amount FLOAT NOT NULL, total_wo_tip FLOAT NOT NULL, ord_no INT NOT NULL AUTO_INCREMENT, PRIMARY KEY (ord_no))"
	mysql -e "$SQL_CMD" -u root $DB_NAME


	echo "Loading data into $FARE_TABLE_NAME"
    SQL_CMD="LOAD DATA LOCAL INFILE '"$fare_f"' IGNORE INTO TABLE "$FARE_TABLE_NAME" 
    FIELDS TERMINATED BY ',' LINES TERMINATED BY '\n' IGNORE 1 LINES 
    (medallion, @hack_license, @vendor_id, pick_date, @payment_type, 
    fare_amount, surcharge, mta_tax, tip_amount, tolls_amount, total_amount) 
	SET total_wo_tip:=total_amount-tip_amount"
    mysql -e "$SQL_CMD" -u root $DB_NAME

	echo "Size:"
	mysql -e "$DB_SZ_COMMAND" -u root $DB_NAME

	echo "Merging fare and trip data into final table $FINAL_TABLE_NAME"

	#Create a new table
	SQL_CMD="CREATE TABLE "$FINAL_TABLE_NAME" SELECT "$TRIP_TABLE_NAME".medallion AS m1,
	"$TRIP_TABLE_NAME".pick_date, "$TRIP_TABLE_NAME".trip_time_in_secs,"$TRIP_TABLE_NAME".trip_distance,"$TRIP_TABLE_NAME".pick_x,  
	"$TRIP_TABLE_NAME".pick_y,"$TRIP_TABLE_NAME".drop_x, "$TRIP_TABLE_NAME".drop_y, "$TRIP_TABLE_NAME".err_flag, 
	"$FARE_TABLE_NAME".total_wo_tip, "$FARE_TABLE_NAME".medallion AS m2, "$FARE_TABLE_NAME".pick_date AS p2,
	"$TRIP_TABLE_NAME".pick_lon, "$TRIP_TABLE_NAME".pick_lat, "$TRIP_TABLE_NAME".drop_lon, "$TRIP_TABLE_NAME".drop_lat, 
	"$TRIP_TABLE_NAME".ord_no 
	FROM "$TRIP_TABLE_NAME"
	JOIN "$FARE_TABLE_NAME" ON "$TRIP_TABLE_NAME".ord_no = "$FARE_TABLE_NAME".ord_no"
	mysql -e "$SQL_CMD" -u root $DB_NAME	
	
	#Add primary key to the new table to speed up updates in python script
	SQL_CMD="ALTER TABLE "$FINAL_TABLE_NAME" ADD PRIMARY KEY (ord_no)"
	mysql -e "$SQL_CMD" -u root $DB_NAME

	#Mark records that do not match - input files are composed such that all rows should match, but this check is just in case misalignment happened
	SQL_CMD="UPDATE "$FINAL_TABLE_NAME" SET err_flag=1 WHERE m1 <> m2 OR pick_date<>p2"
	mysql -e "$SQL_CMD" -u root $DB_NAME

	#Mark records with trip_distance far out of euclidian one
	SQL_CMD="UPDATE "$FINAL_TABLE_NAME" SET err_flag=1 WHERE SQRT(POW(drop_x-pick_x,2) + POW(drop_y-pick_y,2))/trip_distance NOT BETWEEN "$TH_EUCL_DIST_LOW" AND "$TH_EUCL_DIST_UP
	mysql -e "$SQL_CMD" -u root $DB_NAME

	echo "Deleting temp tables"
	SQL_CMD="DROP TABLE "$TRIP_TABLE_NAME
	mysql -e "$SQL_CMD" -u root $DB_NAME
	SQL_CMD="DROP TABLE "$FARE_TABLE_NAME
	mysql -e "$SQL_CMD" -u root $DB_NAME

	echo "Deleting temp columns"
	SQL_CMD="ALTER TABLE "$FINAL_TABLE_NAME" DROP COLUMN m1, DROP COLUMN m2, DROP COLUMN p2"
	mysql -e "$SQL_CMD" -u root  $DB_NAME

	echo "Interim size:"
	mysql -e "$DB_SZ_COMMAND" -u root $DB_NAME

	echo "Deleting marked records"
	SQL_CMD="DELETE FROM "$FINAL_TABLE_NAME" WHERE err_flag=1"
	mysql -e "$SQL_CMD" -u root $DB_NAME

	echo "Invoking python script to mark non Manhattan routes"
	echo $PYTHONPATH
	# python -m $PY_MODULE $TABLE_ID manhattan

	echo "Deleting marked records"
	SQL_CMD="DELETE FROM "$FINAL_TABLE_NAME" WHERE err_flag=1"
	mysql -e "$SQL_CMD" -u root $DB_NAME

	echo "Deleting superfluous columns"
	SQL_CMD="ALTER TABLE "$FINAL_TABLE_NAME" DROP COLUMN ord_no, DROP COLUMN pick_lat, DROP COLUMN pick_lon, DROP COLUMN drop_lat, DROP COLUMN drop_lon"
	mysql -e "$SQL_CMD" -u root  $DB_NAME

	echo "Reclaim free space"
	SQL_CMD="OPTIMIZE TABLE "$FINAL_TABLE_NAME
	mysql -e "$SQL_CMD" -u root  $DB_NAME	

	echo "Adding index: combo 1 point"
	SQL_CMD="ALTER TABLE "$FINAL_TABLE_NAME" ADD INDEX ind_combo (pick_x, pick_y, drop_x, drop_y, pick_date)"
	mysql -e "$SQL_CMD" -u root  $DB_NAME
	
		# echo "Adding index: trip distance"
	# SQL_CMD="ALTER TABLE "$FINAL_TABLE_NAME" ADD INDEX ind_trip_distance (trip_distance)"
	# mysql -e "$SQL_CMD" -u root  $DB_NAME

	# echo "Adding index: trip time"
	# SQL_CMD="ALTER TABLE "$FINAL_TABLE_NAME" ADD INDEX ind_trip_time_in_secs (trip_time_in_secs)"
	# mysql -e "$SQL_CMD" -u root  $DB_NAME

	# echo "Adding index: pick point"
	# SQL_CMD="ALTER TABLE "$FINAL_TABLE_NAME" ADD INDEX ind_pick (pick_x, pick_y)"
	# mysql -e "$SQL_CMD" -u root  $DB_NAME

	# echo "Adding index: drop point"
	# SQL_CMD="ALTER TABLE "$FINAL_TABLE_NAME" ADD INDEX ind_drop (drop_x, drop_y)"
	# mysql -e "$SQL_CMD" -u root  $DB_NAME

	# echo "Adding index: all"
	# SQL_CMD="ALTER TABLE "$TRIP_TABLE_NAME" ADD INDEX ind_all (pick_x, pick_y, drop_x, drop_y, pick_date, drop_date, trip_time_in_secs, trip_distance, pick_lon, pick_lat, drop_lon, drop_lat)"
	# mysql -e "$SQL_CMD" -u root  $DB_NAME

	# echo "Reclaim free space"
	# SQL_CMD="OPTIMIZE TABLE "$FINAL_TABLE_NAME
	# mysql -e "$SQL_CMD" -u root  $DB_NAME

	echo "Final size:"
	mysql -e "$DB_SZ_COMMAND" -u root $DB_NAME

done

#Index test
#EXPLAIN SELECT pick_date FROM trip_2 WHERE pick_x>826.534 AND pick_x>827.0 AND pick_y<-2882.37 AND pick_y>-2883.9 AND drop_x>826.534 AND drop_x>827.0 AND drop_y<-2882.37 AND drop_y>-2883.9 AND pick_date<'2013-02-15' and pick_date>'2013-02-06'
