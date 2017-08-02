# -*- coding: utf-8 -*-
import urllib
import httplib
import json

showapi_appid = '43096'
showapi_sign = '03c3f653ad2741d28989b53fa7b05340'


def fetch_train_time(train_num, more=False):
    params = urllib.urlencode([('showapi_appid', showapi_appid),
                               ('showapi_sign', showapi_sign),
                               ('train_num', train_num.upper())])
    headers = {
        'Content-type': 'application/x-www-form-urlencoded',
        'Accept': 'text/plain'
    }
    conn = httplib.HTTPSConnection('route.showapi.com', port=443, timeout=30)
    conn.request('POST', '/832-2', params, headers)
    str_res = conn.getresponse().read().decode('utf-8')
    json_res = json.loads(str_res)
    conn.close()
    if json_res.get('showapi_res_code') != 0:
        return json_res.get('showapi_res_error')

    res_body = json_res.get('showapi_res_body')
    if not res_body:
        return u'查询失败，请确认车次是否正确。'

    if res_body.get('error_code') != '000':
        return res_body.get('error_description')

    result = u'''{train_type}
始发 {start_station}：{start_time}
到达 {end_station}：{end_time}
历时：{time_all}
全程：{allmile}'''

    result = result.format(train_type=res_body.get('train_type'),
                           start_station=res_body.get('start_station'),
                           start_time=res_body.get('start_time'),
                           end_station=res_body.get('end_station'),
                           end_time=res_body.get('end_time'),
                           time_all=res_body.get('time_all'),
                           allmile=res_body.get('allmile'))

    h = u'{day:<6} 第{num:2}站：{station_name:3} {arrive_time} {leave_time}'
    if more:
        result += '\n'
        for item in res_body.get('data'):
            line = h.format(num=item.get('num'),
                            arrive_time=item.get('arrive_time'),
                            station_name=item.get('station_name'),
                            leave_time=item.get('leave_time'),
                            day=item.get('day'))
            result = '%s%s\n' % (result, line)
    return result


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=u'列车时刻查询')
    parser.add_argument('-n', '--num',
                        dest='train_num',
                        required=True,
                        help=u'列车车次')
    parser.add_argument('-m', '--more',
                        dest='more',
                        action='store_true',
                        default=False,
                        help=u'详情')

    options = parser.parse_args()
    print fetch_train_time(options.train_num.upper(), more=options.more)
