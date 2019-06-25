import dbhelper
import pandas as pd


def split(from_date, to_date):
    sql_split = "select * from public.traffic where time_frame between %s and %s order by timestamp; "
    connection = dbhelper.connect()
    cursor = connection.cursor()
    cursor.execute(sql_split, (from_date, to_date,))
    dataset = cursor.fetchall()
    df = pd.DataFrame(dataset, index=None)
    df.to_csv(from_date+'_'+to_date+'.csv', index=None, header=False)
    print(from_date, to_date, ':', len(dataset))
    return dataset


select_one_day = split('2013-01-07', '2013-01-07')
select_one_week = split('2013-01-07', '2013-01-13')
select_one_month = split('2013-01-01', '2013-01-31')
select_two_month = split('2012-11-05', '2013-01-31')
