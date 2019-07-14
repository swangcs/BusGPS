## data_preprocessing

### Introduction
This directory includes all the scripts that deal with the raw GPS data and output training set for model.

### Instruction
- Run ``pip3 install -r requirements.txt``(python version 3.x) or ``pip install -r requirements.txt`` in terminal to install dependent library.
- Download and install corresponding version of [PostgreSQL](https://www.postgresql.org/download/).
- Run pgAdmin server and replace [configuration](config.ini) with your own configuration, but don't update config.ini file.
- Run [create_tables.sql](create_tables.sql) in the query tool of pgAdmin.
- Import raw GPS and GTFS data to Postgre database.(note: GTFS data is stored as txt format, change it to csv format and it includes header so choose header 'yes')

### Directories
The directories is not exist in the git repository, all data should be imported to postgres database for further using. 
- ``DCC_DublinBusGPSSample_P20130415-0916``: this folder includes one month GPS data downloaded from [Dublin City Council](https://data.smartdublin.ie/dataset/dublin-bus-gps-sample-data-from-dublin-city-council-insight-project)
- ``sir010113-310113``: It is same as above.

### Files
- [count.py](count.py): It count the total points of each bus line and the result is stored in the file [count.csv](count.csv) which has three columns: id, line_id, count.
- [create_tables.sql](create_tables.sql): It will create tables which will be used in the following process. Run the script in the query tool.
- [dbhelper.py](dbhelper.py): It is used to connect postgres database, and change configuration [here](config.ini).
- [extract_route.py](extract_route.py): It is used to extract route which done by methods extract_route_to_json() and get_route_info().
- [plot_route.py](plot_route.py): It plots standard route using dash and plotly. It includes *main* function here.
- [process.py](process.py): It includes a set of basic functions.
- [requirements.txt](requirements.txt): It includes the libraries that the project need to import.
- [split_dataset.py](split_dataset.py): It splits dataset by start date and end date.
- [transform.py](transform.py): It transformed the raw GPS data to separate trajectories list with accumulated travel distance and accumulated time relationship.

### Work
- Run [count.py](count.py), get statical data about total points of each bus line.
- Run [plot_route.py](plot_route.py), get standard traveled distance-time route table of bus line 15(you can change the value of route_short_name to get another route table).
- Run [transform.py](transform.py), 