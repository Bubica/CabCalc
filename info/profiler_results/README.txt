Results of time profiling the data fetch from the local sql db.
Max_samples column indicates the number of records requested for a particular route in the area of certain size around start/end points.
Number_of_records column indicates the number of records retrieved (<= Max_samples requested.
-------------------------------------------------------------------------------------------------------------------------------------
| full_db.csv   		 | Profiling results for searches performed on the whole db. --- disregard this one (index needs to be forced,
|						 | otherwise it's not used -- table scan used instead)
-------------------------------------------------------------------------------------------------------------------------------------
| full_db_forced.csv  	 | Same as full_db.csv, except each SELECT querey had 'ind_combo' forced (i.e. SELECT * FROM trip_x FORCE INDEX
|  						 | (ind_combo) WHERE ... was invoked). ind_combo was created same as in the case of full_db.csv experiment.
-------------------------------------------------------------------------------------------------------------------------------------