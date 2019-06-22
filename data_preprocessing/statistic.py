import process
from matplotlib import pyplot as plt


def plot_hist(d, bins):
    plt.hist(x=d, bins=bins, color='#607c8e', alpha=0.7, rwidth=0.85)
    plt.grid(axis='y', alpha=0.75)
    plt.xlabel('Trip ID')
    plt.ylabel('Points Count')
    plt.title('Distribution of the number of GPS points per trip')
    plt.show()


processed_data = process.load_trip()
nan_trip = {}
trip_count, count, trip_info = [], 0, {'describe': 'lineId#direction#vehicleId#timeFrame#pointsCount'}
for k, v in processed_data.items():
    primary_key = k.split('#')
    if primary_key[0] == 'nan' or primary_key[1] == 'nan' or primary_key[2] == 'nan' or primary_key[3] == 'nan':
        nan_trip[k] = v
    trip_count.extend([count for i in range(len(v))])
    trip_info[count] = k + '#' + str(len(v))
    count += 1
plot_hist(trip_count, [i for i in range(count)])
process.dump_json(trip_info, 'trip.info.json')
process.dump_json(nan_trip, 'nan.20121125.json')
print('Total trips:', len(processed_data.keys()))
print('Total nan trips:', len(nan_trip.keys()))
print('The ratio for missing data is:', len(nan_trip.keys()) / len(processed_data.keys()))
