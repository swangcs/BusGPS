import dbhelper
import json
import process


trips = {}
connection = dbhelper.connect()
cursor = connection.cursor()
select_vehicle_id = "select vehicle_id, count(*) as v_no from public.traffic group by vehicle_id order by v_no"
cursor.execute(select_vehicle_id)
print("Selecting rows from traffic table group by vehicle id using cursor.fetchall")
traffic = cursor.fetchall()
for row in traffic:
    vehicle_id = row[0]
    lon, lat = [], []
    select_position = "select lon, lat from public.traffic where vehicle_id=%s order by timestamp;"
    cursor.execute(select_position, (vehicle_id,))
    positions = cursor.fetchall()
    for p in positions:
        lon.append(p[0])
        lat.append(p[1])
    process.plot_trip_in_line(lon, lat, str(vehicle_id) + ':' + str(len(positions)),
                              file='vehicle/' + str(vehicle_id) + '.png')
    trips[vehicle_id] = {'lon': lon, 'lat': lat}
with open('vehicle.json', 'w') as f:
    json.dump(trips, f)
# primary_key = ['vehicleId', 'journeyId', 'vehicleJourneyId', 'blockId']
# line15 = process.read_csv('line15.csv', sep='\t')
# split(primary_key[:3], line15)
