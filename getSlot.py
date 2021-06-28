#!/bin/python3
import json, requests
import pickle
import datetime,time,os
import pandas as pd

configJson = json.load(open('config.json'))
proxyDict = {
    "http": configJson['proxyserver'],
    "https": configJson['proxyserver'],
}
session_requests = requests.session()
botID=configJson['botID']
chatID=configJson['chatID']


def getLocation(date_object):

    print(date_object)
    pnr_data = {

        'district_id': '303',
        'date': date_object,
    }
    headers = {
        'accept': 'application/json',
        'Accept-Language': 'hi_IN',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'
    }
    url = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/findByDistrict"
    result = session_requests.get(url, headers=headers, params=pnr_data, proxies=proxyDict)
    results = json.loads(result.content)
    #print(results)
    try:
        data = results['sessions']
        URLS = []
        for kk in data:
            # print (kk)
            #print(kk['name'] + " " + str(kk['available_capacity']))
            URLS.append({'name': kk['name'] , 'dose1': kk['available_capacity_dose1'], 'dose2': kk['available_capacity_dose1'],
                         'min_age_limit': kk['min_age_limit'], 'vaccine': kk['vaccine'],'date':kk['date']
                         })

        return URLS
    except Exception as e:
        print(e)
        return False

def getGeoDetails(name):
    try:
     with open('geoDetails.txt', 'rb') as fp:
        geoDetails = pickle.load(fp)
     s1=configJson['source'][0]
     s2=configJson['source'][1]
     for jj in    geoDetails:
        if jj['name']==name:
            return ({s1:jj[s1],s2:jj[s2]})
     return ({'N':'N'})
    except Exception as e:
        print(e)
        return ({'N': 'N'})


def doTheSearchForVaccine():
    configJson = json.load(open('config.json'))
    print ("doing search..")
    loc = []
    if configJson['checkforToday']:
        date_object = datetime.date.today().strftime("%d-%m-%Y")
        loc.extend(getLocation(date_object))
    if configJson['checkforTomorrow']:
        date_object = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%d-%m-%Y")
        loc.extend(getLocation(date_object))
    #print(loc)
    print("Checkin for slots \n\n")
    listofAlerts=[]
    for kk in loc:
        if kk['dose1'] >0:
            if configJson['AlertOnly18']:
                if (kk['min_age_limit'] != 45):
                    kk.update(getGeoDetails(kk['name']))
                    listofAlerts.append(kk)

            else:
               kk.update (getGeoDetails(kk['name']))
               listofAlerts.append(kk)


    if len (listofAlerts) > 0:
        doAlert(listofAlerts)

def  doAlert(obj):
    print ("doing alert")
    df = pd.DataFrame(obj)
    if 'N' in df:
        del df['N']
    #df = df.drop(['N'], axis=1)
    print(df)
    message=df.to_string()[:4000]
    pnr_data = {

        'chat_id': chatID,
        'text': message,
        'parse_mode': 'Markdown'

    }
    headers = {
        'accept': 'application/json',
        'Accept-Language': 'hi_IN',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'
    }
    url = "https://api.telegram.org/bot"+botID+"/sendMessage"
    result = session_requests.get(url, headers=headers, params=pnr_data, proxies=proxyDict)
    results = json.loads(result.content)
    #print(results)
    if (results['ok']):
        return True
    else:
        return False


if __name__ == '__main__':
      while True:
          try:

              doTheSearchForVaccine()
              print ("sleep for  "+ str(configJson['sleepInSec']))
              time.sleep(configJson['sleepInSec'])
          except Exception as e:
              print (e)
