import process
import random


nan_trip = {}
processed_data = process.load_trip()
plot_count = 0
for k, v in processed_data.items():
    primary_key = k.split('#')
    if random.randint(0, 9) == 1 and plot_count < 30:
        plot_count += 1
        if primary_key[0] == 'nan' or primary_key[1] == 'nan' or primary_key[2] == 'nan' or primary_key[3] == 'nan':
            nan_trip[k] = v
        x, y = process.get_x_y(v)
        process.plot_trip_in_line(x, y, k)
process.dump_json(nan_trip, 'nan.20121125.json')
print('Total trips:', len(processed_data.keys()))
print('Total nan trips:', len(nan_trip.keys()))
