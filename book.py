#!/bin/python3
import json, requests
from hashlib import sha256
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
headers = {
    'origin': 'https://selfregistration.cowin.gov.in',
    'referer': 'https://selfregistration.cowin.gov.in/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'
}


def loadPage():
    url = "https://selfregistration.cowin.gov.in/"
    result = session_requests.get(url, headers=headers, proxies=proxyDict)
    print (result.text)

def getOTP():

    pnr_data = {
        "mobile": configJson["mobile"],
        "secret": "U2FsdGVkX1+z/4Nr9nta+2DrVJSv7KS6VoQUSQ1ZXYDx/CJUkWxFYG6P3iM/VW+6jLQ9RDQVzp/RcZ8kbT41xw==",
    }
    url = "https://cdn-api.co-vin.in/api/v2/auth/generateMobileOTP"

    try:
      result = session_requests.post(url,  json=pnr_data,headers=headers, proxies=proxyDict)
      print (result.text)
      results = json.loads(result.content)
      print(results)
      return (results['txnId'])
    except Exception as e:
        print ("Error")
        print (e)

def enterOTP(otp,txnId):

    pnr_data = {
        "otp" : otp,
        "txnId": txnId
    }

    url = "https://cdn-api.co-vin.in/api/v2/auth/validateMobileOtp"
    try:
      print (pnr_data)
      result = session_requests.post(url,  json=pnr_data, headers=headers, proxies=proxyDict)
      #print(result.text)
      results = json.loads(result.content)
      #print(results)
      return  results["token"]
    except Exception as e:
        print (e)

def get_ben():
    url="https://cdn-api.co-vin.in/api/v2/appointment/beneficiaries"
    #print (headers)
    result = session_requests.get(url, headers=headers, proxies=proxyDict)
    if  (result.status_code == 401):
        print(result.text)
        return False
    else:
        results = json.loads(result.content)
        return  results['beneficiaries']


def save_token(token):
    token_file = open("token.txt", 'w')
    token_file.write(token)
    token_file.close()

def read_token():
    token_file = open("token.txt")
    token = token_file.read()
    token_file.close()
    return (token)

def searchCenter():
    date_object = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%d-%m-%Y")
    print(date_object)
    pnr_data = {

        'district_id': '303',
        'date': date_object,
    }


    url = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/findByDistrict"
    result = session_requests.get(url, headers=headers, params=pnr_data, proxies=proxyDict)
    results = json.loads(result.content)
    try:
      data = results['sessions']
      df = pd.DataFrame(data)
      pd.set_option('display.max_rows', df.shape[0] + 1)
      df=df.sort_values(by=['available_capacity'])
      print(df[['name','address','pincode','vaccine','available_capacity','min_age_limit']])
      for kk in data:

        # print (kk)
        # print (kk['name']+" "+  str(kk['available_capacity']))
        center = {}
        if kk['pincode'] in configJson['pincodes']:

            if (configJson['AlertOnly18'] and kk['min_age_limit'] == 45):
                     #print ("skipping {0} {1} ".format((kk['name'],kk['min_age_limit'])))
                      continue

            if kk['available_capacity'] > 1 and kk['vaccine'] == "COVISHIELD":
                center['center_id']= kk['center_id']
                center['session_id']= kk['session_id']
                center['slot']=kk["slots"][-1]
                return  (center)
    except Exception as e:
       print ("BAD")
       print(e)
       return False

def bookSlot(center,benf):
    pnr_data =  {
        "dose": configJson['dose'],
        "session_id":center['session_id'] ,
        "center_id":center['center_id'],
        "slot": center['slot'],
        "beneficiaries":benf
    }
    try:
      url="https://cdn-api.co-vin.in/api/v2/appointment/schedule"
      print (pnr_data)
      result = session_requests.post(url,  json=pnr_data, headers=headers, proxies=proxyDict)
      print(result.text)
      results = json.loads(result.content)
      print(results)
    except Exception as e:
        print (e)


if __name__ == '__main__':
    token = read_token()
    headers.update({'Authorization': f"Bearer {token}"})
    if get_ben():
        print ("token is valid ")
    else:
      del headers['Authorization']
      txnId=getOTP()
      otp=input("Enter OTP :")
      myotp = sha256(str(otp.strip()).encode("utf-8")).hexdigest()
      token=enterOTP(myotp,txnId)
      save_token(token)
      headers.update({'Authorization': f"Bearer {token}"})
    benfs=[]
    for kk in get_ben():
        benfs.append((kk['beneficiary_reference_id']))
        print ("{0}  {1}".format(kk['beneficiary_reference_id'],kk['name']))
    centerDetails=searchCenter()
    if (centerDetails):
        if (configJson['readBenfFromCowin']):
            bookSlot(centerDetails, benfs)
        else:
           bookSlot(centerDetails,configJson["beneficiaries"])



## 