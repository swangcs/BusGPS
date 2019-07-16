import process
import pandas
import os
from dbhelper import connect


def count_dir(path_dir):
    sum_lines = 0
    files = process.get_files(path_dir)
    for file in files:
        f = path_dir + '/' + file
        print(f)
        # no head exist, using ',' as separator, rename the index, set null value as Na
        raw_data = process.read_csv(f)
        for row in raw_data.itertuples(index=True, name='Pandas'):
            sum_lines += 1
            bus_line_id = getattr(row, 'lineId')
            if bus_line_id not in bus_line_count:
                bus_line_count[bus_line_id] = 0
            bus_line_count[bus_line_id] += 1
        print(sum_lines)
    return sum_lines


if __name__ == '__main__':
    '''
    Count the total points of each line in raw dataset
    If the directories are exist, there load the data from the directories, else connect to database and launch a query.
    '''
    bus_line_count = {}
    data_dir1, data_dir2 = 'DCC_DublinBusGPSSample_P20130415-0916', 'sir010113-310113'
    if os.path.exists(data_dir1) and os.path.exists(data_dir2):
        sum_ = count_dir(data_dir1) + count_dir(data_dir2)
        bus_line_count = sorted(bus_line_count.items(), key=lambda i: i[1], reverse=True)
        df = {'line id': [], 'count': []}
        for (k, v) in bus_line_count:
            df['line id'].append(k)
            df['count'].append(v)
        df = pandas.DataFrame(df)
        df.to_csv('count.csv', decimal=',')
        print(sum_)
    else:
        connector = connect()
        cursor = connector.cursor()
        cursor.execute("select line_id, count(line_id) as count from busGPS group by line_id order by count desc;")
        bus_line_count = cursor.fetchall()
        df = pandas.DataFrame(bus_line_count)
        df.to_csv('count.csv', header=['line_id', 'count'], sep=',')

