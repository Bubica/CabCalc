#!/bin/bash 

#Random downsampling of data in local mysql db
#NOTE: 
#This script uses err flag column to set mark the records that were not sampled (value=1). 
#Previous values of err column will be discarded.

source db_setup.sh
SAMPLE_PERC=0.5 #percentage of samples that will be kept in the database - random sampling

for i in {6..12}
do
	TABLE_NAME=$TABLE_PREFIX$i

	#Check if the table exists in the db
	SQL_CMD="SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = '"$DB_NAME"' AND table_name = '"$TABLE_NAME"'"
	exists=`mysql -s -N -e "$SQL_CMD" -u root  $DB_NAME`

	if [ $exists -eq 0 ]
	then 
		echo "No data for month $i"
		continue	
	fi

	echo "Updating month $i" 

	echo "Size @ the beginning: "
	mysql -e "$DB_SZ_COMMAND" -u root $DB_NAME

	TABLE_NAME=$TABLE_PREFIX$i
	SQL_CMD="UPDATE "$TABLE_NAME" SET err_flag=IF(RAND()<="$SAMPLE_PERC", 0, 1)"
	mysql -e "$SQL_CMD" -u root  $DB_NAME

	echo "Delete marked records..." 
	SQL_CMD="DELETE FROM "$TABLE_NAME" WHERE err_flag=1"
	mysql -e "$SQL_CMD" -u root  $DB_NAME

	echo "Cleanup..."
	#Drop indices
	./db_indexing.sh drop $TABLE_NAME

	echo "Reclaim free space"
	SQL_CMD="OPTIMIZE TABLE "$TABLE_NAME
	mysql -e "$SQL_CMD" -u root  $DB_NAME

	#Recreate indices
	./db_indexing.sh create $TABLE_NAME

	echo "Size @ the end: "
	mysql -e "$DB_SZ_COMMAND" -u root $DB_NAME

done

