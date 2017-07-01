#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re # 正则表达式
import requests
from pprint import pprint

url = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.9017'
response = requests.get(url, verify=False)
stations = re.findall(u'([\u4e00-\u9fa5]+)\|([A-Z]+)', response.text) # findall以列表形式返回数据，用括号来捕获分组
pprint(dict(stations), indent=4)