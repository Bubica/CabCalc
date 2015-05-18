#Load the basic setup
source db_setup.sh

#Add extra boolean column
for TRIP_ID in `seq 1 12`;
do
	TRIP_TABLE="trip_"$TRIP_ID

    #Create extra columns in trip table (if not already present)
    # SQL_CMD="ALTER TABLE "$TRIP_TABLE" ADD COLUMN manhattan TINYINT(1)"
    # mysql -e "$SQL_CMD" -u root  $DB_NAME

    python -m $PY_MODULE $TRIP_ID manhattan
    
done
