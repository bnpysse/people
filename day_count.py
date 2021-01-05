# 按日期检索文章的篇数
#
from requests import exceptions
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
    # '_ga': 'GA1.2.576373095.1589077068',
    # 只需要改这个东东就可以，2020-06-11 17:14:42
    'JSESSIONID': '8D88531154544921063069167EDE01E2',
    'ezproxy': '6AydvMiD22cUvI5',
}
login_url = 'http://data.people.com.cn.proxy.library.georgetown.edu/rmrb/20200702/1?code=2'
login_headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu '
                               'Chromium/68.0.3440.106 Chrome/68.0.3440.106 Safari/537.36',
                 'Content-Type': 'text/html;charset=UTF-8', }

# base_url = 'http://data.people.com.cn.proxy.library.georgetown.edu/rmrb/s?type=2&qs='
base_url = 'http://data.people.com.cn.proxy.library.georgetown.edu/rmrb/{}/1'
query_date = '1993-01-01'
database_name = 'article_count.db'
qs = {"cds": [{"fld": "dataTime", "cdr": "AND", "hlt": "false", "vlr": "OR", "qtp": "DEF", "val": query_date}],
      "obs": [{"fld": "dataTime", "drt": "DESC"}]}

login_s = requests.session()
cookies = requests.utils.cookiejar_from_dict(login_cookies_dict)
try:
    resp = login_s.get(login_url, headers=login_headers, cookies=cookies)
    if resp.status_code == 429:
        print('429 Error, It''s end')
        exit(1)
except Exception as e:
    print('Error: {}'.format(e))


def get_count(year, month):
    start_time = datetime.now()
    url_list = get_day_url(year, month)
    for k, v in enumerate(url_list):
        start_month_time = datetime.now()
        try:
            html = login_s.get(url_list[k]['URL'], headers=login_headers, cookies=cookies).content.decode('utf-8')
        except exceptions.HTTPError as e:
            print(f'http error:{e.message}')
            break
        except exceptions.Timeout as e:
            print(f'请求超时:{e.message}')
            break
        doc = pq(html)
        # url_list[k]['Count'] = int(doc('#allDataCount').text())
        url_list[k]['Count'] = int(doc('#UseRmrbNum').text())
        url_list[k]['LayoutNumber'] = int(doc('#UseRmrbPageNum').text())
        k += 1
    minutes, secs = divmod((datetime.now() - start_time).seconds, 60)
    print(f'Processing..{year}年{month:2d}月,累计用时：{minutes:2d}分{secs:2d}秒')
    return url_list


def get_day_url(year, month):
    date_list = [{} for i in range(calendar.monthrange(year, month)[1])]
    k = 0
    for i in range(calendar.monthrange(year, month)[1]):
        str2 = str(year) + '-' + str("%02d" % month) + '-' + str("%02d" % (i+1))
        today = datetime.now().today()
        if datetime.strptime(str2, '%Y-%m-%d') > today:
            break
        str1 = f'{year}{month:02d}{i + 1:02d}'

        qs['cds'][0]['val'] = str1
        # date_list[k]['URL'] = base_url + urllib.parse.quote(str(qs).replace(' ', '').replace('\'', '\"'))

        date_list[k]['URL'] = base_url.format(str1)
        date_list[k]['Date'] = str2
        k += 1
    return date_list


def writeMonth(year, *args):
    if len(args) == 2:
        # 起始月份，终止月份
        start_month = args[0] if args[0] > 0 else 1
        end_month = args[1] if args[1] < 13 else 12
    sql_insert = 'INSERT INTO `article_count_new`(Date,Count,LayoutNumber) values("{}",{},{})'
    for month in range(start_month, end_month + 1):
        url_list = get_count(year, month)
        create_sqlite_db()
        conn = sqlite3.connect(database_name)
        cursor = conn.cursor()
        cursor.execute('begin transaction')
        for k, v in enumerate(url_list):
            if 'Date' in v.keys():
                cursor.execute(sql_insert.format(v['Date'], v['Count'], v['LayoutNumber']))
        cursor.execute('commit')
        cursor.close()
        conn.close()


def create_sqlite_db():
    sql = 'CREATE TABLE if not exists `article_count_new`( `id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, `Date` ' \
          'TEXT, `Count` INTEGER, `LayoutNumber` INTEGER)'
    # delete_sql = 'drop table {}'
    conn = sqlite3.connect(database_name)
    cur = conn.cursor()
    cur.execute(sql)
    cur.close()
    conn.commit()
    conn.close()


def writeYear(year):
    start_time = datetime.now()
    for month in range(1, 13):
        start_month_time = datetime.now()
        writeMonth(year, month)
        print(f'Processing..{year}年{month:2d}月，用时：{(datetime.now() - start_month_time).seconds:3d}，'
              f'累计用时：{(datetime.now() - start_time).seconds:3d}')


if __name__ == '__main__':
    # writeYear(1993)
    writeMonth(2020, 1, 6)
