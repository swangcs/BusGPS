-- create tables using scripts and then insert csv file into postgres database
CREATE TABLE busGPS(timestamp bigint,line_id varchar(10), direction int,journey_pattern_id varchar(10),time_frame varchar(15),
vehicle_journey_id int,operator varchar(5),congestion int,lon float, lat float,delay int,block_id int,vehicle_id int,stop_id varchar(10),at_stop int);
create table trips(route_id varchar(20),service_id char(1),trip_id varchar(50),
				   shape_id varchar(50),trip_headsign varchar(100),direction_id char(1));
create table routes(route_id varchar(20),route_short_name varchar(10),route_long_name varchar(100),route_type char(1));
create table stop_times(trip_id varchar(50),arrival_time varchar(20),departure_time varchar(20),stop_id varchar(20),
stop_sequence varchar(10),pickup_type varchar(10),drop_off_type varchar(10),shape_dist_traveled varchar(50));
create table stops(stop_id varchar(20),stop_name varchar(100),stop_lat varchar(50),stop_lon varchar(50));
create table shapes(shape_id varchar(30),shape_pt_lat varchar(30),shape_pt_lon varchar(30),
shape_pt_sequence varchar(10),shape_dist_traveled varchar(30));
