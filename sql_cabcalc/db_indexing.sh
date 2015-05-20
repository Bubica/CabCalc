#!/bin/bash 

#Load the basic setup
source db_setup.sh
	

for TRIP_ID in `seq 1 12`;
do
	TRIP_TABLE="trip_"$TRIP_ID

	echo "Adding index: combo 1 point to "$TRIP_TABLE
	SQL_CMD="ALTER TABLE "$TRIP_TABLE" ADD INDEX ind_combo (pick_x, pick_y, drop_x, drop_y, pick_date)"
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
    
done

