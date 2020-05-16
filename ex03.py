import requests
from pyquery import PyQuery as pq
import os
import datetime
import time
import bs4

login_cookies_dict = {
    # 'JSESSIONID': 'E1CBA10B637794FA770DC61CB0DCE91A',
    '_ga': 'GA1.2.576373095.1589077068',
    # 'targetEncodinghttp://127001': '2',
    'ezproxy': 'GdTowbJgi0ObdIv',
}

# login_url = 'https://login.proxy.library.georgetown.edu/connect?session=s9ynQXhvukC5r0GT&qurl=http%3a%2f%2fdata.people.com.cn%2frmrb%2f20200510%2f1'
url = 'http://data.people.com.cn.proxy.library.georgetown.edu/rmrb/s?type=2&qs=%7B%22cds%22%3A%5B%7B%22fld%22%3A%22dataTime.start%22%2C%22cdr%22%3A%22AND%22%2C%22hlt%22%3A%22false%22%2C%22vlr%22%3A%22AND%22%2C%22qtp%22%3A%22DEF%22%2C%22val%22%3A%22{}%22%7D%2C%7B%22fld%22%3A%22dataTime.end%22%2C%22cdr%22%3A%22AND%22%2C%22hlt%22%3A%22false%22%2C%22vlr%22%3A%22AND%22%2C%22qtp%22%3A%22DEF%22%2C%22val%22%3A%22{}22%7D%5D%2C%22obs%22%3A%5B%7B%22fld%22%3A%22dataTime%22%2C%22drt%22%3A%22ASC%22%7D%5D%7D'
login_url = 'http://data.people.com.cn.proxy.library.georgetown.edu/rmrb/20200515/1?code=2'

login_headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/68.0.3440.106 Chrome/68.0.3440.106 Safari/537.36',
                 'Content-Type': 'text/html;charset=UTF-8',}

login_s = requests.session()
cookies = requests.utils.cookiejar_from_dict(login_cookies_dict)
resp = login_s.get(login_url, headers=login_headers, cookies=cookies)

doc = pq(str(resp.content, 'utf-8'))

url = 'http://data.people.com.cn.proxy.library.georgetown.edu/rmrb/s?type=2&qs=%7B%22cds%22%3A%5B%7B%22fld%22%3A%22dataTime.start%22%2C%22cdr%22%3A%22AND%22%2C%22hlt%22%3A%22false%22%2C%22vlr%22%3A%22AND%22%2C%22qtp%22%3A%22DEF%22%2C%22val%22%3A"{}"7D%2C%7B%22fld%22%3A%22dataTime.end%22%2C%22cdr%22%3A%22AND%22%2C%22hlt%22%3A%22false%22%2C%22vlr%22%3A%22AND%22%2C%22qtp%22%3A%22DEF%22%2C%22val%22%3A"{}"7D%5D%2C%22obs%22%3A%5B%7B%22fld%22%3A%22dataTime%22%2C%22drt%22%3A%22ASC%22%7D%5D%7D'

params = {
    'type': '2',
    'qs': '{"cds":[{"fld":"dataTime.start","cdr":"AND","hlt":"false","vlr":"AND","qtp":"DEF","val":"2000-01-01"},'
          '{"fld":"dataTime.end","cdr":"AND","hlt":"false","vlr":"AND","qtp":"DEF","val":"2000-02-01"}],'
          '"obs":[{"fld":"dataTime","drt":"ASC"}]',
}

status_url = 'http://data.people.com.cn.proxy.library.georgetown.edu/member/loginStatus'

def fetchUrl(url):
    headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
               'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/68.0.3440.106 Chrome/68.0.3440.106 Safari/537.36',
               'Content-Type': 'text/html;charset=UTF-8', }
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    r.encoding = r.apparent_encoding
    return r.text

