#!/bin/bash 

#Load the basic setup
source db_setup.sh

WEATHER_TABLE_NAME=weather

# Create the weather table
SQL_CMD="CREATE TABLE IF NOT EXISTS "$WEATHER_TABLE_NAME" (time DATETIME NOT NULL, station CHAR(5) NOT NULL, temperature FLOAT, dew FLOAT, humidity FLOAT, pressure FLOAT, visibility FLOAT, wind_dir CHAR(10), wind FLOAT, gust FLOAT, precip_float FLOAT, precip_bool TINYINT(1), events CHAR(15), conditions CHAR(50));"
mysql -e "$SQL_CMD" -u root  $DB_NAME

# Extrapolating only data from the Central Park weather station to all NYC points - erroneous but simple
for f in $WEATHER_CSV_DIR/weather_nyc_KNYC*.csv
do
	SPLIT=(${f//_/ })
	STATION=${SPLIT[3]}
	
	#Create boolean indicator if there was any rain or snow for the given record
	SQL_CMD="LOAD DATA LOCAL INFILE '"$f"' INTO TABLE "$WEATHER_TABLE_NAME" FIELDS TERMINATED BY ',' LINES TERMINATED BY '\n' IGNORE 1 LINES (time, temperature, dew, humidity, pressure, visibility, wind_dir, wind, gust, @fprecip, @fevents, @fconditions) 
	SET  
	station:='KYNC', 
	events:= nullif(@fevents,'None'), 
	conditions:= nullif(@fconditions,'None'), 
	precip_float:=nullif(@fprecip,'None'),
	precip_bool := IF((events IS NULL AND precip_float<0.5) OR events = 'Fog', 0,1);"
	mysql -e "$SQL_CMD" -u root  $DB_NAME

done


SQL_CMD="ALTER TABLE "$WEATHER_TABLE_NAME" ADD INDEX ind_time (time)"
mysql -e "$SQL_CMD" -u root  $DB_NAME



# #v2
# CREATE TABLE IF NOT EXISTS test (time DATETIME NOT NULL, station CHAR(20) NOT NULL, temperature FLOAT, dew FLOAT, humidity FLOAT, pressure FLOAT, visibility FLOAT, wind_dir CHAR(10), wind FLOAT, gust FLOAT, precip_float FLOAT, precip_bool TINYINT(1), events CHAR(15), conditions CHAR(20));
# LOAD DATA LOCAL INFILE 'weather_nyc_KNYC_2013_4_10.csv' INTO TABLE test FIELDS TERMINATED BY ',' LINES TERMINATED BY '\n' IGNORE 1 LINES (time, temperature, dew, humidity, pressure, visibility, wind_dir, wind, gust, @fprecipitation, @fevents, @fconditions) 
# SET  
# station:='KYNC', 
# events:= nullif(@fevents,'NULL'), 
# conditions:= nullif(@fconditions,'NULL'),  
# precip_float:=nullif(@fprecipitation,''),
# precip_bool := IF(events IS NULL OR events = 'Fog', 0,1);


# #Join with trip data and store result in trip table
# ALTER TABLE trip_2 ADD COLUMN precip_f FLOAT, ADD COLUMN precip_b TINYINT(1);
# SELECT * FROM trip_2 JOIN (SELECT time, precipitation, precip_bool FROM weather WHERE)

# UPDATE trip_2 SET precip_f='k1', col_b='foo' WHERE key_col='1';

SELECT  (
SELECT precip_float
FROM weather
ORDER BY ABS(TIMESTAMPDIFF(MINUTE, time, pick_date))
LIMIT 1)
FROM trip_2
LIMIT 10

