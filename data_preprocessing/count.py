import os
import process
import pandas


def get_files(path):
    return os.listdir(path)


def count_dir(path_dir):
    files = get_files(path_dir)
    for file in files:
        f = path_dir + '/' + file
        print(f)
        # no head exist, using ',' as separator, rename the index, set null value as Na
        raw_data = process.read_csv(f)
        for row in raw_data.itertuples(index=True, name='Pandas'):
            bus_line_id = getattr(row, 'lineId')
            if bus_line_id not in bus_line_count:
                bus_line_count[bus_line_id] = 0
            bus_line_count[bus_line_id] += 1


bus_line_count = {}
count_dir('DCC_DublinBusGPSSample_P20130415-0916')
count_dir('sir010113-310113')
bus_line_count = sorted(bus_line_count.items(), key=lambda i: i[1], reverse=True)
df = {'line id': [], 'count': []}
for (k, v) in bus_line_count:
    df['line id'].append(k)
    df['count'].append(v)
df = pandas.DataFrame(df)
df.to_csv('count.csv')
