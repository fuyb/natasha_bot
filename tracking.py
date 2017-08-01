#!/usr/bin/env python
#!encoding: utf-8
import json
import urllib
import base64
import httplib
import md5
import argparse

KDNIAO_APP_ID = '1298806'
KDNIAO_KEY = '57f61425-ca2f-4a19-882a-751e609ce74a'

def request_api(params, request_type):
    params_md5 = md5.new(json.dumps(params) + KDNIAO_KEY).hexdigest()
    data_sign = base64.b64encode(params_md5) 
    data = {
        'RequestData': json.dumps(params),
        'RequestType': request_type,
        'DataSign': data_sign,
        'DataType': '2',
        'EBusinessID': KDNIAO_APP_ID,
    }

    headers = {'Content-type': 'application/x-www-form-urlencoded'}
    uri = '/Ebusiness/EbusinessOrderHandle.aspx'
    conn = httplib.HTTPConnection(host='api.kdniao.cc', port=80, timeout=60)
    data = urllib.urlencode(data)
    conn.request('POST', uri, data, headers)
    response = conn.getresponse()
    resp_data = None
    if response.status == 200:
        try:
            resp_data = json.loads(response.read())
        except Exception as e:
            print unicode(e)
            resp_data = {'error': -1}
    return resp_data

def tracking(shipper_code, tracking_number):
    params = {
        'ShipperCode': shipper_code,
        'LogisticCode': tracking_number,
        'OrderCode': '',
    }
    return request_api(params, '1002')

def fetch_shipper_code(tracking_number):
    params = {
        'LogisticCode': tracking_number,
    }
    return request_api(params, '2002')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=u'查询快递信息')

    # Output verbosity options.
    parser.add_argument('-s', '--shipper',
                        dest='shipper_code',
                        help=u'快递公司编号')
    parser.add_argument('-n', '--number',
                        dest='number',
                        required=True,
                        help=u'快递单编号')
    options = parser.parse_args()
    shipper_code = options.shipper_code
    number = options.number

    if shipper_code is None:
        resp_data = fetch_shipper_code(options.number)
        if resp_data.get('error') or not resp_data.get('Success'):
            print u'查询失败，请确认快递单编号是否正确。:)'.encode('utf-8', 'ignore')
            exit(-1)
        shipper_code = resp_data.get('Shippers')[0].get('ShipperCode')

    resp_data = tracking(shipper_code, number)
    if resp_data.get('error'):
        print u'查询失败，请确认快递单编号是否正确。:)'.encode('utf-8', 'ignore')
        exit(-1)

    if not resp_data.get('Success') or resp_data.get('State') not in ('2', '3', '4'):
        ret = u"%s，请确认快递单编号是否正确。:)" % resp_data.get('Reason')
        print ret.encode('utf-8', 'ignore')
        exit(-1)

    for line in ["%s %s" % (item.get('AcceptStation'), item.get('AcceptTime')) 
            for item in resp_data.get('Traces')]:
        print line.encode('utf-8', 'ignore')
