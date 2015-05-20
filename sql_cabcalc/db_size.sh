source db_setup.sh

DB_SZ_COMMAND="SELECT * FROM (SELECT table_schema \"DBName\",     Round(Sum(data_length + index_length) / 1024 / 1024, 1) \"DB Size in MB\"  FROM   information_schema.tables  GROUP  BY table_schema) AS total WHERE DBName=\""$DB_NAME"\""

function print_db_size 
{
	# Print out the current size of the database
	echo "Curr size:"
	mysql -e "$DB_SZ_COMMAND" -u root $DB_NAME
}