## data_preprocessing

### Introduction
This directory includes all the scripts that deal with the raw GPS data and output training set for model.

### Instruction
- Run ``pip3 install -r requirements.txt``(python version 3.x) or ``pip install -r requirements.txt`` in terminal to install dependent library.
- Download and install corresponding version of [PostgreSQL](https://www.postgresql.org/download/).
- Run pgAdmin server and replace [configuration](config.ini) with your own configuration, but don't update config.ini file.
- Run [create_tables.sql](create_tables.sql) in the query tool of pgAdmin.
- Import raw GPS and GTFS data to Postgre database.(note: GTFS data is stored as txt format, change it to csv format and it includes header so choose header 'yes')

### Files
- [count.py](count.py): It counts the total points of each bus line and the result is stored in the file [count.csv](count.csv) which has three columns: id, line_id, count.
- [create_tables.sql](create_tables.sql): It creates tables which will be used in the following process. Run the script in the query tool.
- [dbhelper.py](dbhelper.py): It is used to connect postgres database, and change configuration [here](config.ini).
- [plot_route.py](plot_route.py): It plots standard route using dash and plotly.
- [utils.py](utils.py): It includes a set of basic functions that used to deal with some common problems(such as calculating distance)
- [requirements.txt](requirements.txt): It includes the libraries that the project need to import.
- [split_dataset.py](split_dataset.py): It splits dataset by start date and end date.
- [transform.py](transform.py): It transforms the raw GPS data to separate trajectories list with accumulated travel distance and accumulated time relationship.
- [plot_trajectories](plot_trajectories.py): It plots trajectories using dash and plotly.
- [prepare_training_set.py](prepare_training_set.py): It creates training sets for model training.

### Work
- Run [count.py](count.py), get statical data about total points of each bus line.
- Run [plot_route.py](plot_route.py), plot standard accumulated traveled distance-time route table of bus line 15(you can change the value of route_short_name to get another route table).
- Run [transform.py](transform.py), transform raw GPS data to separate trajectories with accumulated distance and time.
- Run [plot_trajectories.py](plot_trajectories.py), plot change of accumulated traveled distance-time table of trajectories according to route_short_name(set '15' as default).
- Run [prepare_training_set.py](prepare_training_set.py), prepare training sets and it will be stored in [training_sets.json](../model_training/training_sets.json). It records accumulated time every meter.
