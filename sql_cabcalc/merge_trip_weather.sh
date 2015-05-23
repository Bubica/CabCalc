#!/bin/bash 

#Load the weather data into trip table 

#Load the basic setup
source db_setup.sh

for TRIP_ID in `seq 10 10`;
do
	TRIP_TABLE="trip_"$TRIP_ID

    #Create extra columns in trip table (if not already present)
    # SQL_CMD="ALTER TABLE "$TRIP_TABLE" ADD COLUMN precip_f FLOAT, ADD COLUMN precip_b TINYINT(1)"
    # mysql -e "$SQL_CMD" -u root  $DB_NAME

    python -m $PY_MODULE $TRIP_ID weather
    
done



