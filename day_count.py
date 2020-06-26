# 按日期检索文章的篇数

import itertools
import math
import re
import sqlite3
import urllib.parse
from datetime import datetime
import calendar
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

base_url = 'http://data.people.com.cn.proxy.library.georgetown.edu/rmrb/s?type=2&qs='
query_date = '1993-01-01'
database_name = 'article_count.db'
qs = {"cds": [{"fld": "dataTime", "cdr": "AND", "hlt": "false", "vlr": "OR", "qtp": "DEF", "val": query_date}],
      "obs": [{"fld": "dataTime", "drt": "DESC"}]}

login_s = requests.session()
cookies = requests.utils.cookiejar_from_dict(login_cookies_dict)
login_s.get(login_url, headers=login_headers, cookies=cookies)


def get_count(year, month):
    url_list = get_day_url(year, month)
    for k, v in enumerate(url_list):
        html = login_s.get(url_list[k]['URL'], headers=login_headers, cookies=cookies).content.decode('utf-8')
        doc = pq(html)
        url_list[k]['Count'] = int(doc('#allDataCount').text())
        k += 1
    return url_list


def get_day_url(year, month):
    date_list = [{} for i in range(calendar.monthrange(year, month)[1])]
    k = 0
    for i in range(calendar.monthrange(year, month)[1]):
        # str1 = str(year) + '-' + str("%02d" % month) + '-' + str("%02d" % (i+1))
        str1 = f'{year}-{month:02d}-{i + 1:02d}'
        qs['cds'][0]['val'] = str1
        date_list[k]['URL'] = base_url + urllib.parse.quote(str(qs).replace(' ', '').replace('\'', '\"'))
        date_list[k]['Date'] = str1
        k += 1
    return date_list


def writeMonth(year, month):
    sql_insert = 'INSERT INTO `article_count`(Date,Count) values("{}",{})'
    url_list = get_count(year, month)
    create_sqlite_db()
    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()
    cursor.execute('begin transaction')
    for k, v in enumerate(url_list):
        cursor.execute(sql_insert.format(v['Date'], v['Count']))
    cursor.execute('commit')
    cursor.execute('end transaction')


def create_sqlite_db():
    sql = 'CREATE TABLE if not exists `article_count`( `id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, `Date` ' \
          'TEXT, `Count` INTEGER)'
    # delete_sql = 'drop table {}'
    conn = sqlite3.connect(database_name)
    cur = conn.cursor()
    cur.execute(sql)
    cur.close()
    conn.commit()
    conn.close()


def writeYear(year):
    for month in range(1, 13):
        writeMonth(year, month)


if __name__ == '__main__':
    writeMonth(1993)
