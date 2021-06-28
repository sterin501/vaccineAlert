import json, requests
import pickle
import datetime,time,os
import pandas as pd


session_requests = requests.session()
date_object = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%d-%m-%Y")
print(date_object)
headers = {
    'origin': 'https://selfregistration.cowin.gov.in',
    'referer': 'https://selfregistration.cowin.gov.in/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'
}


pnr_data = {
        'district_id': '303',
        'date': date_object,
    }
url = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/findByDistrict"
result = session_requests.get(url, headers=headers, params=pnr_data)
results = json.loads(result.content)

print (results)
