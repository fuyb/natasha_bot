#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
import httplib
import json

appkey = '7fdb2ccc23243093dff2fc9e4f4ac4a5'

def qa_request(message, uid):
    params = {
        'key': appkey,
        'info': message,
        'dtype': 'json',
        'userid': uid 
    }
    params = urllib.urlencode(params)
    headers = {'Content-type': 'application/x-www-form-urlencoded', 'Accept': 'text/plain'}
    conn = httplib.HTTPSConnection('op.juhe.cn', port=443, timeout=30)
    conn.request('POST', '/robot/index', params, headers)
    str_res = conn.getresponse().read().decode('utf-8')
    json_res = json.loads(str_res)
    conn.close()
    return json_res

def qa_request_text(message, uid):
    data = qa_request(message, uid)
    print data
    if data.get('error_code') != 0:
        return ':)'
    result = data.get('result')
    return result.get('text').replace(u'聚合数据', ' Natasha ')

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=u'聊天机器人')
    parser.add_argument('-m', '--message',
                        dest='message',
                        required=True,
                        help=u'消息')
    parser.add_argument('-u', '--uid',
                        dest='uid',
                        required=True,
                        help=u'用户id')
    options = parser.parse_args()
    print qa_request_text(options.message, options.uid)
