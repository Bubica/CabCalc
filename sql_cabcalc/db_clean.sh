#!/bin/bash 

#Load the basic setup
source db_setup.sh

echo "Deleting marked records"

for TRIP_ID in `seq 1 12`;
do
	TRIP_TABLE="trip_"$TRIP_ID

	echo "Editing table "$TRIP_TABLE

	# echo "Deleting erroneous records..."
	# SQL_CMD="DELETE FROM "$TRIP_TABLE" WHERE err_flag=1"
	# mysql -e "$SQL_CMD" -u root $DB_NAME

	echo "Deleting superfluous columns"
	SQL_CMD="ALTER TABLE "$TRIP_TABLE" DROP COLUMN err_flag, DROP COLUMN pick_lat, DROP COLUMN pick_lon, DROP COLUMN drop_lat, DROP COLUMN drop_lon, DROP COLUMN precip_b, DROP COLUMN ord_no, DROP COLUMN manhattan"
	mysql -e "$SQL_CMD" -u root  $DB_NAME

	echo "Reclaim free space"
	# SQL_CMD="OPTIMIZE TABLE "$TRIP_TABLE
	# mysql -e "$SQL_CMD" -u root  $DB_NAME

	echo "Curr size:"
	mysql -e "$DB_SZ_COMMAND" -u root $DB_NAME

done

echo "Deleting weather table"
SQL_CMD="DROP TABLE IF EXISTS "$WEATHER_TABLE_NAME
mysql -e "$SQL_CMD" -u root  $DB_NAME

# echo "Reclaim free space"
# SQL_CMD="OPTIMIZE TABLE "$TRIP_TABLE
# mysql -e "$SQL_CMD" -u root  $DB_NAME

echo "Curr size:"
mysql -e "$DB_SZ_COMMAND" -u root $DB_NAME

