#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import urllib
import httplib
import string
import argparse

from datetime import datetime, timedelta

def format_time(ms):
    _time = timedelta(milliseconds=ms)
    _datetime = datetime(1, 1, 1) + _time
    return "%.2d:%.2d:%.2d" % (_datetime.hour, _datetime.minute, _datetime.second)

def search(query, only_one=True):
    data = {
        'limit': '10',
        'offset': '0',
        's': query,
        'total': 'true',
        'type': '1',
    }

    headers = {
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.8,gl;q=0.6,zh-TW;q=0.4',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Host': 'music.163.com',
        'Referer': 'http://music.163.com/search/',
        'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.152 Safari/537.36',
    }
    uri = '/api/search/get'
    conn = httplib.HTTPConnection(host='music.163.com', port=80, timeout=60)
    data = urllib.urlencode(data)
    conn.request('POST', uri, data, headers)
    response = conn.getresponse()
    resp_data = None
    if response.status == 200:
        try:
            content = response.read()
            resp_data = json.loads(content)
        except Exception as e:
            print unicode(e)
            resp_data = {'error': -1}
    if only_one:
        try:
            song = resp_data.get('result').get('songs')[0]
            song_url = 'http://music.163.com/#/song?id=%s' % song.get("id")
            artists = song.get('artists')
            artist_list = list()
            for art in artists:
                artist_list.append(art.get('name'))
            info = "%s < %s > by %s / %s / %s" % (song.get("name"),
                    song_url,
                    string.join(artist_list, ','),
                    song.get('album').get('name'),
                    format_time(song.get('duration')))
            return info
        except Exception as e:
            print e
            return ''
    return resp_data


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=u'music.163.com搜歌')

    # Output verbosity options.
    parser.add_argument('-q', '--query',
                        dest='query',
                        required=True,
                        help=u'歌曲名字')
    options = parser.parse_args()
    query = options.query

    if query is not None:
        resp_data = search(options.query)
        print resp_data
