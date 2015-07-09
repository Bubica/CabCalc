#!/bin/bash 

#Load the basic setup
source db_setup.sh
	

for TRIP_ID in `seq 1 12`;
do
	TRIP_TABLE=$TABLE_PREFIX$TRIP_ID

	echo "Adding index ind_combo to "$TRIP_TABLE
	SQL_CMD="ALTER TABLE "$TRIP_TABLE" ADD INDEX ind_combo (pick_x, pick_y, drop_x, drop_y, pick_date)"
	mysql -e "$SQL_CMD" -u root  $DB_NAME
    
done

#Print out the current size of DB
mysql -e "$DB_SZ_COMMAND" -u root  $DB_NAME

