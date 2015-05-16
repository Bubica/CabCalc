#!/bin/bash 

#Load the weather data into trip table 

#Load the basic setup
source db_setup.sh

for trip_id in `seq 1 12`;
do
	TRIP_TABLE="trip_"$trip_id

    #Create extra columns in trip table (if not already present)
    SQL_CMD="ALTER TABLE "$TRIP_TABLE" ADD COLUMN precip_f FLOAT, ADD COLUMN precip_b TINYINT(1)"
    mysql -e "$SQL_CMD" -u root  $DB_NAME

done 

# UPDATE trip_2 SET precip_f= (SELECT  (SELECT precip_float
# FROM weather
# ORDER BY ABS(TIMESTAMPDIFF(MINUTE, time, pick_date))
# LIMIT 1)
# FROM trip_2)
# WHERE key_col='1';
# done   


# CREATE TEMPORARY TABLE IF NOT EXISTS trip_2_weather AS
# (
# SELECT pick_date, (SELECT precip_float
# FROM weather
# ORDER BY ABS(TIMESTAMPDIFF(MINUTE, time, pick_date))
# LIMIT 1) AS precip_f
# FROM trip_2
# )