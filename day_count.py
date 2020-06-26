# 按日期检索文章的篇数

import itertools
import math
import re
import sqlite3
import urllib.parse
from datetime import datetime
import pprint
import requests
from pyquery import PyQuery as pq

# region 更改 cookie 值，每次当程序不能正确运行时，需要修改这里的 ezproxy
# 获取正确的对话 login_session
login_cookies_dict = {
     '_ga': 'GA1.2.576373095.1589077068',
     # 只需要改这个东东就可以，2020-06-11 17:14:42
     'ezproxy': '2BY4iVSZv25bVX2',
}
login_url = 'http://data.people.com.cn.proxy.library.georgetown.edu/rmrb/20200515/1?code=2'
login_headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu '
                               'Chromium/68.0.3440.106 Chrome/68.0.3440.106 Safari/537.36',
                 'Content-Type': 'text/html;charset=UTF-8', }

query_date = '1993-01-01'
qs = {"cds": [{"fld": "dataTime", "cdr": "AND", "hlt": "false", "vlr": "OR", "qtp": "DEF", "val": query_date}],
     "obs": [{"fld": "dataTime", "drt": "DESC"}]}

login_s = requests.session()
cookies = requests.utils.cookiejar_from_dict(login_cookies_dict)
login_s.get(login_url, headers=login_headers, cookies=cookies)

def get_count(qry_date):

