import requests
from pyquery import PyQuery as pq
import os
from datetime import datetime, timedelta
import bs4
import math
import csv

login_cookies_dict = {
    # 'JSESSIONID': 'E1CBA10B637794FA770DC61CB0DCE91A',
    '_ga': 'GA1.2.576373095.1589077068',
    # 'targetEncodinghttp://127001': '2',
    # 需要改的就是这个东西
    'ezproxy': 'X62pZXETTLJvhvK',
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
    link_dict = [dict() for i in range(pageSize)]
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
    start_date, end_date = get_month_begin_end_day(month)
    html, totalPageNum = getPeriod(start_date, end_date, 1)
    print('totalPageNum:{}'.format(totalPageNum))
    for i in range(2, totalPageNum + 1):
        searchDict = parseSearch(html)
        print('Processing..第{}页'.format(i - 1))
        # 写入到 csv 文件中去，还是写入到sqlite数据库？2020-05-18 18:15:007
        with open(month + '.csv', 'a+') as file:
            w = csv.writer(file)
            for k, v in enumerate(searchDict):
                if 'Title' in searchDict[k].keys():
                    # w.writerow(searchDict[k]['Title'], searchDict[k]['Date'], searchDict[k]['Layout'],
                    #            searchDict[k]['Keywords'], searchDict[k]['Summary'], searchDict[k]['Link'])
                    w.writerow(searchDict[k].values())
        html, total = getPeriod(start_date, end_date, i)


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
def getDetail(link_dict):
    for k, v in enumerate(link_dict):
        resp = login_s.get(link_dict[k]['Link'], headers=login_headers, cookies=cookies)
        html = str(resp.content, 'utf-8')
        doc = pq(html)
        print(doc('.detail_con').text())


if __name__ == '__main__':
    # html, totalPageNum = getPeriod('2000-01-01', '2000-02-01', 68)
    # l = parseSearch(html)
    #
    # for k, v in enumerate(l):
    #     if 'Title' in l[k].keys():
    #         print(k, ':', l[k]['Title'], ':', l[k]['Date'], ':第', l[k]['Layout'], '版', ':', l[k]['Keywords'],
    #               '\n\t', l[k]['Summary'], ':', l[k]['Link'])
    writeMonth('200001')
