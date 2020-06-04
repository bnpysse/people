# 2020-06-03 21:32:34 似乎找到了新的方法，是可以获取到2003年之后的详情，而且不需要用到
# 验证码，不知道这算不算一个Bug，不管它了，嘿嘿
# 即：在查询的结果中添加这样的参数 &position=XX ,代表了查询结果中第 0 篇到 PageSize-1的详情
# 页面，这个结果还是相当不错的，所以把原来的程序改一下，应该就可以用了。

import sqlite3
import requests
from pyquery import PyQuery as pq
import os
from datetime import datetime, timedelta
import math
import csv

login_cookies_dict = {
    # 'JSESSIONID': 'E1CBA10B637794FA770DC61CB0DCE91A',
    '_ga': 'GA1.2.576373095.1589077068',
    # 'targetEncodinghttp://127001': '2',
    # 需要改的就是这个东西
    'ezproxy': 'CZ8jzZRc7trPiXx',
}

login_url = 'http://data.people.com.cn.proxy.library.georgetown.edu/rmrb/20200515/1?code=2'

login_headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu '
                               'Chromium/68.0.3440.106 Chrome/68.0.3440.106 Safari/537.36',
                 'Content-Type': 'text/html;charset=UTF-8', }

status_url = 'http://data.people.com.cn.proxy.library.georgetown.edu/member/loginStatus'
base_url = 'http://data.people.com.cn.proxy.library.georgetown.edu'
pageSize = 50
login_s = requests.session()
cookies = requests.utils.cookiejar_from_dict(login_cookies_dict)
login_s.get(login_url, headers=login_headers, cookies=cookies)

url = 'http://data.people.com.cn.proxy.library.georgetown.edu/rmrb/s?qs=%7B%22cds%22%3A%5B%7B%22fld%22%3A%22dataTime' \
      '.start%22%2C%22cdr%22%3A%22AND%22%2C%22hlt%22%3A%22false%22%2C%22vlr%22%3A%22AND%22%2C%22qtp%22%3A%22DEF%22%2C' \
      '%22val%22%3A%22{}%22%7D%2C%7B%22fld%22%3A%22dataTime.end%22%2C%22cdr%22%3A%22AND%22%2C%22hlt%22%3A' \
      '%22false%22%2C%22vlr%22%3A%22AND%22%2C%22qtp%22%3A%22DEF%22%2C%22val%22%3A%22{}%22%7D%5D%2C%22obs%22' \
      '%3A%5B%7B%22fld%22%3A%22dataTime%22%2C%22drt%22%3A%22ASC%22%7D%5D%7D&tr=A&ss=1&pageNo={}&pageSize={}'

detail_url = \
    'http://data.people.com.cn.proxy.library.georgetown.edu/rmrb/s?qs=%7B%22cds%22%3A%5B%7B%22fld%22%3A%22dataTime' \
    '.start%22%2C%22cdr%22%3A%22AND%22%2C%22hlt%22%3A%22false%22%2C%22vlr%22%3A%22AND%22%2C%22qtp%22%3A%22DEF%22%2C' \
    '%22val%22%3A%22{}%22%7D%2C%7B%22fld%22%3A%22dataTime.end%22%2C%22cdr%22%3A%22AND%22%2C%22hlt%22%3A' \
    '%22false%22%2C%22vlr%22%3A%22AND%22%2C%22qtp%22%3A%22DEF%22%2C%22val%22%3A%22{}%22%7D%5D%2C%22obs%22' \
    '%3A%5B%7B%22fld%22%3A%22dataTime%22%2C%22drt%22%3A%22ASC%22%7D%5D%7D&tr=A&ss=1&pageNo={}&pageSize={}&position={}'


# 每页的链接是动态生成的，只能通过计算来获得总页数，在查询出来的页面中是不含总页数的，只有allDataCount这个总的记录条数
# 2020-05-17 01:44:08
def getPeriod(start_date, end_date, pageNo):
    # start_date:起始日期
    # end_date:终止日期,格式必须是 YYYYMMDD
    resp = login_s.get(url.format(start_date, end_date, pageNo, pageSize), headers=login_headers, cookies=cookies)
    html = str(resp.content, 'utf-8')
    # #allDataCount记录的是总的记录数,始终向上取整，即183.2页，也应该取到184页才对 2020-05-17 00:43:40
    # .open_detail_link 是当前搜索结果页条目的 html 标志符
    # len(doc('.open_detail_link')) = 50,即我们把一页搜索结果设置为50条
    # 同时可以得到总的页数
    doc = pq(html)
    totalPageNum = math.ceil(int(doc('#allDataCount').text()) / pageSize)
    return html, totalPageNum


# 对查询的结果页面进行处理，每页50条
def parseSearch(html):
    doc = pq(html)
    link_dict = [dict() for i in range(pageSize + 1)]
    for k, v in enumerate(doc('.open_detail_link').items()):
        link_dict[k]['Title'] = v.text()
        link_dict[k]['Link'] = base_url + v.attr('href')

    # 从[浏览本版]链接中可以获得日期，及版面
    for k, v in enumerate(doc('.listinfo a').items()):
        link_dict[k]['Date'] = v.attr('href').split('/')[2]
        link_dict[k]['Layout'] = v.attr('href').split('/')[3]

    for k, v in enumerate(doc('.keywords').items()):
        tmp = v.text().split('：')[1].lstrip(' ')
        link_dict[k]['Keywords'] = tmp.replace(' ', ',')

    for k, v in enumerate(doc('.sreach_li p').items()):
        link_dict[k]['Summary'] = v.text()

    return link_dict


# 按月份建立数据库，取得某个月的起始日期，然后写到以月份命名的sqlite库中
def writeMonth(month):
    insert_sql = 'insert into `{}`(Title, Date, Layout, Keywords, Summary, Link) values("{}","{}","{}","{}","{}","{}")'
    createSqlite(month)
    conn = sqlite3.connect(month[:4] + '.db')
    cursor = conn.cursor()
    start_time = datetime.now()
    start_page_time = datetime.now()
    start_date, end_date = get_month_begin_end_day(month)

    html, totalPageNum = getPeriod(start_date, end_date, 1)
    print('totalPageNum:{}'.format(totalPageNum))
    for i in range(2, totalPageNum + 2):
        searchDict = parseSearch(html)
        # 写入到 csv 文件中去，还是写入到sqlite数据库？2020-05-18 18:15:007
        # with open(month + '.csv', 'a+') as file:
        #     w = csv.writer(file)
        #     for k, v in enumerate(searchDict):
        #         if 'Title' in searchDict[k].keys():
        #             # w.writerow(searchDict[k]['Title'], searchDict[k]['Date'], searchDict[k]['Layout'],
        #             #            searchDict[k]['Keywords'], searchDict[k]['Summary'], searchDict[k]['Link'])
        #             w.writerow(searchDict[k].values())
        cursor.execute('begin transaction')
        for k, v in enumerate(searchDict):
            if 'Title' in searchDict[k].keys():
                cursor.execute(insert_sql.format(month, searchDict[k]['Title'], searchDict[k]['Date'],
                                                 searchDict[k]['Layout'],
                                                 searchDict[k]['Keywords'], searchDict[k]['Summary'],
                                                 searchDict[k]['Link']))

        cursor.execute('commit')
        print('Processing..第{}页,用时：{:5.2f}秒'.format(i - 1, (datetime.now() - start_page_time).seconds))
        start_page_time = datetime.now()
        html, total = getPeriod(start_date, end_date, i)
    cursor.close()
    conn.close()
    print('处理{}年{}月,累计用时：{:5.2f} 秒'.format(month[:4], month[4:], (datetime.now() - start_time).seconds))


# 可以一次取一年的，哈哈, 2020-05-20 12:08:24，今天试验的效果一般，只取到5月份的，看来取一年的还是不行，主要是网络不行
def writeYear(year):
    for i in range(1, 13):
        print('正在处理 {} 年 {} 月'.format(year, i))
        month = year + '{:02d}'.format(i)
        writeMonth(month)


# 创建一个空数据库
def createSqlite(month):
    sql = 'CREATE TABLE if not exists `{}`( `id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, `Title` TEXT, `Link` TEXT, `Date` ' \
          'TEXT, `Layout` TEXT, `Keywords` TEXT, `Summary` TEXT )'
    # delete_sql = 'drop table {}'
    db_file_name = month[:4] + '.db'
    conn = sqlite3.connect(db_file_name)
    cur = conn.cursor()
    cur.execute(sql.format(month))
    cur.close()
    conn.commit()
    conn.close()


# 获取某个月份的起止日期字符串
def get_month_begin_end_day(month):
    month_begin_day = month + "01"
    next_month = int(month) + 1
    if next_month % 100 == 13:
        next_month = next_month - 12 + 100
    month_end_day = (datetime(int(str(next_month)[0:4]), int(str(next_month)[4:6]), 1) - timedelta(days=1)).strftime(
        "%Y%m%d")
    return month_begin_day, month_end_day


# 对每一页的结果，获取详细内容
# 2020-05-21 06:35:05 做了修改，直接打开数据库，把保存的 Link 取出，获得详情
def getDetail(month):
    sql_str = 'select id,Title,Link from `{}` limit {},{};'
    db_file_name = month[:4] + '.db'
    if os.path.exists(db_file_name):
        conn = sqlite3.connect(db_file_name)
    else:
        exit()
    cursor = conn.cursor()
    conn.row_factory = sqlite3.Row
    count = cursor.execute('select count(*) from `{}`;'.format(month)).fetchone()[0]
    for page in range(0, math.ceil(count / pageSize)):
        rows = cursor.execute(sql_str.format(month, page * pageSize, pageSize)).fetchall()
        for row in rows:
            # print(row[0], row[1])
            resp = login_s.get(row[1], headers=login_headers, cookies=cookies)
            html = str(resp.content, 'utf-8')
            doc = pq(html)
            # 取出具体内容后还需要到数据库中j
            print(doc('.detail_con').text())


if __name__ == '__main__':
    # html, totalPageNum = getPeriod('2000-01-01', '2000-02-01', 68)
    # l = parseSearch(html)
    #
    # for k, v in enumerate(l):
    #     if 'Title' in l[k].keys():
    #         print(k, ':', l[k]['Title'], ':', l[k]['Date'], ':第', l[k]['Layout'], '版', ':', l[k]['Keywords'],
    #               '\n\t', l[k]['Summary'], ':', l[k]['Link'])
    # writeMonth('198012')
    # writeYear('1980')
    # getDetail('197801')
    for year in range(1982, 1990):
        writeYear(str(year))
