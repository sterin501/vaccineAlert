#!/bin/python3
import json, requests
import pickle
import haversine as hs
import pandas as pd


configJson = json.load(open('config.json'))
proxyDict = {
    "http": configJson['proxyserver'],
    "https": configJson['proxyserver'],
}
apikey = configJson['geoKey']
session_requests = requests.session()


def getGeoLock(place):
    pnr_data = {

        'access_token': apikey,
        'limit': '1'
    }
    headers = {
        'accept': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'
    }
    url = "https://api.mapbox.com/geocoding/v5/mapbox.places/" + place + ".json"
    result = session_requests.get(url, headers=headers, params=pnr_data, proxies=proxyDict)
    # result=session_requests.get("https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/findByDistrict?district_id=303&date=26-05-2021")
    results = json.loads(result.content)
    #print(results)
    #print (results['center'])
    try:
        s = (results['features'][0]['center'])
        return (str(s[0]) + "," + str(s[1]))

    except:
        return (False)

def getDistance(source,dest):
    s1= (float(n) for n in source.split(','))
    d1= (float(n) for n in dest.split(','))
    return round(hs.haversine(s1,d1),2)

if __name__ == '__main__':
    with open('location.txt', 'rb') as fp:
        itemlist = pickle.load(fp)
    with open('geoDetails.txt', 'rb') as fp:
        cachelist = pickle.load(fp)
    checklist=list(itemlist)
    # for i in cachelist:
    #     if  i['name'] in itemlist:
    #         checklist.remove(i['name'] )

    listLocation=[]
    for kk in (checklist):
        #st= (kk.replace(' ','+'))
        st  = kk.split(' ')[0]
        if len(st) == 1:
           st=kk.split(' ')[1]
        listLocation.append({'name':kk,'geo':getGeoLock(st)})
    print (listLocation)
    sourceGeo=[]
    for jj in configJson['source']:
        sourceGeo.append({'placeName':jj,'geo':getGeoLock(jj)})

    for kk in listLocation:
      if not kk['geo']:
          continue
      for jj in  (sourceGeo):
         distance= ( getDistance(kk['geo'],jj['geo']))
         kk.update({jj['placeName']:distance})
    print (listLocation)
    df = pd.DataFrame(listLocation)
    print(df)
    df.sort_values(configJson['source'][0]).to_csv('listIn.csv', index=False)
    with open('geoDetails.txt', 'wb') as fp:
        pickle.dump(listLocation, fp)

