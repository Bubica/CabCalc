#!/bin/bash 

#Load the basic setup
source db_setup.sh

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
	precip_float:= IF(@fprecip='None',0, @fprecip),
	precip_bool := IF(precip_float>0.5 OR events LIKE '%Rain%' OR events LIKE '%Snow%', 1,0);"
	mysql -e "$SQL_CMD" -u root  $DB_NAME

done


SQL_CMD="ALTER TABLE "$WEATHER_TABLE_NAME" ADD INDEX ind_time (time)"
mysql -e "$SQL_CMD" -u root  $DB_NAME





