USE taxi;

# Debuging 
# check the duration of query execution

#Original query
RESET QUERY CACHE;
SET profiling = 1; 

SELECT pick_date, drop_date, trip_time_in_secs, trip_distance, pick_lon, pick_lat, drop_lon, 
drop_lat, err_flag, total_wo_tip 
FROM trip_4 AS trip 
JOIN fare_4 AS fare ON fare.medallion = trip.medallion AND fare.pickup_datetime=trip.pick_date 
WHERE pick_x BETWEEN 826.949772 AND 827.749772 AND pick_y BETWEEN -2883.886784 AND -2883.086784 AND drop_x BETWEEN 826.960650 AND 827.760650 AND drop_y BETWEEN -2882.801018 AND -2882.001018;

SHOW PROFILES; #Duration 96.90436800, 100.08310800

RESET QUERY CACHE;
SELECT pick_date, drop_date, trip_time_in_secs, trip_distance, pick_lon, pick_lat, drop_lon, 
drop_lat, err_flag, total_wo_tip 
FROM trip_4 AS trip 
JOIN fare_4 AS fare ON fare.medallion = trip.medallion AND fare.pickup_datetime=trip.pick_date 
WHERE pick_x > 826.949772 AND pick_x< 827.749772 AND pick_y > -2883.886784 AND pick_y< -2883.086784 AND drop_x > 826.960650 AND drop_x< 827.760650 AND drop_y > -2882.801018 AND drop_y < -2882.001018;

SHOW PROFILES; #Duration 89


ALTER TABLE trip_4 ADD INDEX ind_pick_y (pick_y);
ALTER TABLE trip_4 ADD INDEX ind_drop_y (drop_y);

SELECT pick_date, drop_date, trip_time_in_secs, trip_distance, pick_lon, pick_lat, drop_lon, 
drop_lat, err_flag, total_wo_tip 
FROM trip_4 AS trip 
JOIN fare_4 AS fare ON fare.medallion = trip.medallion AND fare.pickup_datetime=trip.pick_date 
WHERE pick_x > 826.949772 AND pick_x< 827.749772 AND pick_y > -2883.886784 AND pick_y< -2883.086784 AND drop_x > 826.960650 AND drop_x< 827.760650 AND drop_y > -2882.801018 AND drop_y < -2882.001018;

SHOW PROFILES; #Duration 101.68092000

ALTER TABLE trip_4 ADD INDEX ind_xy (pick_x, pick_y, drop_x, drop_y);
ALTER TABLE trip_4 ADD INDEX ind_all (pick_x, pick_y, drop_x, drop_y, pick_date, drop_date, trip_time_in_secs, trip_distance, pick_lon, pick_lat, drop_lon, 
drop_lat);

SELECT pick_date, drop_date, trip_time_in_secs, trip_distance, pick_lon, pick_lat, drop_lon, 
drop_lat, total_wo_tip 
FROM trip_4 AS trip 
JOIN fare_4 AS fare ON fare.medallion = trip.medallion AND fare.pickup_datetime=trip.pick_date 
WHERE pick_x > 826.949772 AND pick_x< 827.749772 AND pick_y > -2883.886784 AND pick_y< -2883.086784 AND drop_x > 826.960650 AND drop_x< 827.760650 AND drop_y > -2882.801018 AND drop_y < -2882.001018;

FORCE INDEX (ind_pick, ind_drop)
SHOW PROFILES; #38.02832900


ALTER TABLE trip_2 ADD INDEX ind_all (pick_x, pick_y, drop_x, drop_y, pick_date, drop_date, trip_time_in_secs, trip_distance, pick_lon, pick_lat, drop_lon, 
drop_lat);

SELECT pick_date, drop_date, trip_time_in_secs, trip_distance, pick_lon, pick_lat, drop_lon, 
drop_lat, err_flag, total_wo_tip FROM trip_7 AS trip JOIN fare_7 AS fare 
ON fare.medallion = trip.medallion AND fare.pickup_datetime=trip.pick_date 
WHERE pick_x BETWEEN 827.099772 AND 827.599772 AND pick_y BETWEEN -2883.736784 
AND -2883.236784 AND drop_x BETWEEN 827.110650 AND 827.610650 AND drop_y BETWEEN -2882.651018 
AND -2882.151018 LIMIT 5000



