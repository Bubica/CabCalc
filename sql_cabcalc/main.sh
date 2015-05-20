#!/bin/bash 

#Load the data from trip and fare files into the local mysql db
# source loader_trip_fare.sh

#Load the weather data into the separate table
# source loader_weather.sh

#Merge weather and trip data
# source merge_trip_weather.sh

#Merge mark Manhattan routes
# source manhattan.sh

#Delete interim data
# source db_clean.sh

#Build indices
# source db_indexing.sh

#Print out size
source db_size.sh
print_db_size
