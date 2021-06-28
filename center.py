#!/usr/bin/python
import urllib, urllib2, cookielib,re




opener = urllib2.build_opener()

def get_center():
    pnr_data = urllib.urlencode({       'district_id': '306',
                                        'date': '26-05-2021'
    })
    print(pnr_data)
    resp = opener.open('https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/findByDistrict', pnr_data)
    print(resp.read())



if __name__ == '__main__':
    get_center()
