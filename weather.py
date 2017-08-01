#!encoding: utf-8
import requests
from const_value import API, KEY, UNIT, LANGUAGE
import json

def fetch_weather(location):
    result = requests.get(API, params={
        'key': KEY,
        'location': location,
        'language': LANGUAGE,
        'unit': UNIT,
        'daily': 3
    }, timeout=1)
    data = json.loads(result.text)
    if data:
        results = data.get('results')
        if results:
            now = results[0].get('now')
            result = u'{city}\n天气：{weather}\n气温：{temperature}°C'.format(
                    city=location,
                    weather=now.get('text'),
                    temperature=now.get('temperature'))
            return result
    return u'查询天气失败，或不支持这个城市'
