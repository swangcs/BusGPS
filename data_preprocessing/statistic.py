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
trip_count, count, trip_info = [], 0, {'describe': 'lineId#direction#vehicleId#timeFrame#pointsCount'}
for k, v in processed_data.items():
    primary_key = k.split('#')
    trip_count.extend([count for i in range(len(v))])
    trip_info[count] = k + '#' + str(len(v))
    count += 1
plot_hist(trip_count, [i for i in range(count)])
process.dump_json(trip_info, 'trip.info.json')
