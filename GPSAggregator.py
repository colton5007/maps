import requests
import json
import time
import pickle

X_ECM_API_ID = "ea38ba46-045b-42b4-905a-bdb7a6112729"
X_ECM_API_KEY = "017ab8409aa1604a217e8903681e86ecb33a5a14"
X_CP_API_ID = "c58eb0ce"
X_CP_API_KEY = "8786e65e28a2ab0ad4b3074799b05b43"
group_id = 114394

headers = {
	'X-CP-API-ID': X_CP_API_ID,
	'X-CP-API-KEY': X_CP_API_KEY,
	'X-ECM-API-ID': X_ECM_API_ID,
	'X-ECM-API-KEY': X_ECM_API_KEY,
	'Content-Type': 'application/json' 
}

def create_gps_json():
	temp = "markers = "
	arr = list()
	for key in routers:
		arr.append(routers[key])
	temp += json.dumps(arr)
	with open("maps/markers.json", 'w+') as f:
		f.write(temp)

# Get routers
routers = dict()
try:
	f = open("cache.pkl", "rb")
	routers = pickle.load(f)
except Exception as e:
	routers = dict()
routers = dict()

def update(device_id, asset_id=None, lat=None, lon=None):
	if device_id not in routers:
		lat = 0
		lon = 0
		routers[device_id] = {
			"lat": lat,
			"lon": lon,
			"asset_id": asset_id
		}
	if lat and lon:
		routers[device_id] = {
			"lat": lat,
			"lon": lon,
			"asset_id": asset_id
		}

while True:
	router_url = 'https://www.cradlepointecm.com/api/v2/routers/'
	location_url = 'https://www.cradlepointecm.com/api/v2/locations/'

	while router_url:
		req = requests.get(router_url, headers=headers)
		routers_resp = req.json()
		if req.status_code != 200:
			print(routers_resp)
		else:
			data = routers_resp['data']
			for r in data:
				try:
					if r['group'] and str(group_id) in r['group']:
						update(r['id'], r['asset_id'])
						# routers.append(r)
				except Exception as e:
					print(e)
					print(r)
					print(data)
			# Get URL for next set of resources
			router_url = routers_resp['meta']['next']

	# print("Done fetching routers")

	while location_url:
		req = requests.get(location_url, headers=headers)
		location_resp = req.json()
		if req.status_code != 200:
			print(location_resp)
		else:
			data = location_resp['data']
			for r in data:
				i = r['router'].replace("https://www.cradlepointecm.com/api/v2/routers/", '').replace('/','')
				# print("Updating lat lon for " + i)
				if i in routers:
					routers[i]['lat'] = r['latitude']
					routers[i]['lon'] = r['longitude']
			# Get URL for next set of resources
			location_url = routers_resp['meta']['next']

	create_gps_json()
	print("Updated GPS")
	
	f = open("cache.pkl", "wb+")
	pickle.dump(routers, f)
	f.close()

	time.sleep(60)