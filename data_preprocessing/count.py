import pandas
from data_preprocessing.dbhelper import connect


if __name__ == '__main__':
    '''
    Count the total points of each line in raw dataset
    If the directories are exist, there load the data from the directories, else connect to database and launch a query.
    '''
    connector = connect()
    cursor = connector.cursor()
    cursor.execute("select trajid, count(*) as count from busgps group by trajid order by trajid;")
    bus_line_count = cursor.fetchall()
    df = pandas.DataFrame(bus_line_count)
    df.to_csv('count_RIO.csv', header=['line_id', 'count'], sep=',')
    # df.to_csv('count.csv', header=['line_id', 'count'], sep=',')
