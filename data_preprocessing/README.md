## data_preprocessing

### Introduction
This directory includes all the scripts that deal with the raw GPS data and output training set for model.

### Directories
The directories is not exist in the git repository, all data should be imported to postgres database for further using. 
- ``DCC_DublinBusGPSSample_P20130415-0916``: this folder includes one month GPS data downloaded from [Dublin City Council](https://data.smartdublin.ie/dataset/dublin-bus-gps-sample-data-from-dublin-city-council-insight-project)
- ``sir010113-310113``: It is same as above

### Files
- [count.py](count.py): It count the total points of each bus line and the result is stored in the file [count.csv](count.csv) which has three columns: id, line_id, count.
- [create_tables.sql](create_tables.sql): It will create tables which will be used in the following process. Run the script in the query tool.
- [dbhelper.py](dbhelper.py): It is used to connect postgres database, and change configuration [here](config.ini)

