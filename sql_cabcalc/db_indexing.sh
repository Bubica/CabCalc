#!/bin/bash 

#Load the basic setup
source db_setup.sh

#Create/destroy table indices
if [ $1 = "create" ];
then 

	TABLE_NAME=$2

	echo "Adding index for table $TABLE_NAME combo 1 point"
	SQL_CMD="ALTER TABLE "$TABLE_NAME" ADD INDEX ind_combo (pick_x, pick_y, drop_x, drop_y, pick_date)"
	mysql -e "$SQL_CMD" -u root  $DB_NAME
	

elif [ $1 = "drop" ];
then
	echo "Dropping indices for $2"

	TABLE_NAME=$2

	SQL_CMD="ALTER TABLE "$TABLE_NAME" DROP INDEX ind_combo"
	mysql -e "$SQL_CMD" -u root  $DB_NAME

else
	echo "Supported options: create/drop."
fi