#!/bin/python3
import  json,requests
import pickle
import datetime


configJson=json.load(open('config.json'))
proxyDict = {
  "http" : configJson['proxyserver'] ,
  "https":configJson['proxyserver'],
}
session_requests = requests.session()

def getLocation():
  #date_object = datetime.date.today().strftime("%d-%m-%Y")
  date_object = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%d-%m-%Y")
  print(date_object)
  pnr_data =                 {

                            'district_id'      : '303',
                            'date' : date_object,
                              }
  headers = {
             'accept': 'application/json',
             'Accept-Language':'hi_IN',
              'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'
            }
  url="https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/findByDistrict"
  result = session_requests.get(url,headers=headers,params=pnr_data,proxies=proxyDict)
  #result=session_requests.get("https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/findByDistrict?district_id=303&date=26-05-2021")
  results = json.loads(result.content)
  print (results)
  try:
     data = results['sessions']
     URLS=[]
     for kk in data:
        #print (kk)
        #print (kk['name']+" "+  str(kk['available_capacity']))
        URLS.append (kk['name'])

     return URLS
  except Exception as e:
     print (e)
     return False

if __name__ == '__main__':
    loc=getLocation()
    print (loc)
    with open('location.txt', 'wb') as fp:
        pickle.dump(loc, fp)