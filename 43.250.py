# 又发现一个新的数据库 http://43.250.238.143.proxy.library.georgetown.edu/101.jsp 看从这个库中能不能获取更多的信息
# 2020-06-23 13:20:44
import itertools
import math
import re
import sqlite3
import urllib.parse
from datetime import datetime
import pprint
import requests
from pyquery import PyQuery as pq

login_url = 'http://data.people.com.cn.proxy.library.georgetown.edu/publish/_s1/0819.html'

base_url = 'http://43.250.238.143.proxy.library.georgetown.edu'
base_url1 = 'http://43.250.238.143.proxy.library.georgetown.edu/images/300/316/316.jsp'

# 列表页，参数为 页码 和 年份+月份
outline_url = 'http://43.250.238.143.proxy.library.georgetown.edu/outline?page={}&channelid={}'

# 详情页，参数为记录的ID号 和 年份+月份
detail_url = 'http://43.250.238.143.proxy.library.georgetown.edu/download_log.jsp?dbname=%C8%CB%C3%F1%C8%D5%B1%A8%CD%BC%CE%C4%CA%FD%BE%DD%C8%AB%CE%C4%BC%EC%CB%F7%CF%B5%CD%B3&record={}&channelid={}'

# detail_url = 'http://43.250.238.143.proxy.library.georgetown.edu/download_log.jsp?dbname=%C8%CB%C3%F1%C8%D5%B1%A84&record={}&channelid={}'

search_url = 'http://43.250.238.143.proxy.library.georgetown.edu/search?channelid={}'

login_cookies_dict = {
    'ezproxy': '2BY4iVSZv25bVX2',
    # 'pass': '11%2C101%2C103%2C104%2C105%2C107%2C114%2C129%2C',
    # 'userid': 'georgetownuc',
    # 'username': 'Georgetown%2BUniversity',
    # 'Hm_lpvt_fea96aed2ece526c02d508e0b9ab0c79': '1593107790',
    # 'Hm_lvt_fea96aed2ece526c02d508e0b9ab0c79': '1593105751',
    'JSESSIONID': '0DC80BD210222684BD70E542FBC55BAB',
}
login_headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu '
                               'Chromium/68.0.3440.106 Chrome/68.0.3440.106 Safari/537.36',
                 'Content-Type': 'text/html;charset=UTF-8',
                 }
login_s = requests.session()
pageSize = 50


def writeMonth(ym, content_dict, rec_id):
    insert_sql = '''
        insert into `{}`(Title, Date, Layout, LayoutName, IntroTitle, SubTitle, Writer, Content) values('{}','{}',{},'{}','{}','{}', '{}','{}')
    '''
    create_sqlite_db(ym)
    conn = sqlite3.connect(ym[:4] + '.db')
    cursor = conn.cursor()
    cursor.row_factory = sqlite3.Row
    cursor.execute('begin transaction')
    try:
        for k, v in enumerate(content_dict):
            if 'Title' in v.keys():
                cursor.execute(
                    insert_sql.format(ym, v['Title'], v['Date'], v['Layout'], v['LayoutName'], v['IntroTitle'],
                                      v['SubTitle'],
                                      v['Writer'], v['Content']))
        cursor.execute('commit')
    except Exception as e:
        print(f'RecNo is {rec_id}, Error is {e}')
        cursor.execute('rollback')
    cursor.close()
    conn.close()


def create_sqlite_db(ym):
    sql = 'CREATE TABLE if not exists `{}`( `id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, `Title` TEXT, `Date` ' \
          'TEXT, `IntroTitle` TEXT, `SubTitle` INTEGER, `Layout` INTEGER, `LayoutName` Text, `Writer` TEXT, `Content` Text)'
    # delete_sql = 'drop table {}'
    conn = sqlite3.connect(ym[:4] + '.db')
    cur = conn.cursor()
    cur.execute(sql.format(ym))
    cur.close()
    conn.commit()
    conn.close()


def get_last_rec(ym):
    conn = sqlite3.connect(ym[:4] + '.db')
    cursor = conn.cursor()
    cursor.row_factory = sqlite3.Row
    result = cursor.execute(
        'select count(*) as count from sqlite_master where type="table" and name="{}"'.format(ym)).fetchone()
    if result['count'] == 0:
        count = 0
    else:
        result = cursor.execute('select seq from sqlite_sequence where name="{}"'.format(ym)).fetchone()
        count = int(result['seq'])
    cursor.close()
    conn.close()
    return count


def get_month(ym):
    start_month_time = datetime.now()
    html = login_s.get(search_url.format(ym), headers=login_headers,
                       cookies=requests.utils.cookiejar_from_dict(login_cookies_dict)).content.decode('gb18030')
    doc = pq(html)
    # 读出数据库中已存的记录，得做比较。因为可能会有错误发生，就应该接着上次出错的位置去做
    last_rec = get_last_rec(ym)
    total_rec = int(doc('.DropShadow14').text().split('\n')[1])
    start_rec = 0
    if last_rec < total_rec:
        start_rec = last_rec
    print('处理{}年{}月数据，数据库中已有{:^4d}条记录，共{:^4d}条记录'.format(ym[:4], ym[4:], last_rec, total_rec))
    content_dict = [{} for i in range(pageSize)]
    start_page_time = datetime.now()
    # 计数器，每到50个那么就写入一次数据库，原来用的是 (rec+1)%(pageSize+1) 来进行判断，是不对的，执行一次就会加1 。。。
    # 2020-06-25 23:04:59
    for rec in range(start_rec, total_rec):
        if (rec + 1) % pageSize != 0:
            analy_detail(content_dict, rec, ym)
        else:
            # 不添加这些的话，会读不到被 pageSize 整除的那些记录的。2020-06-26 00:30:59
            # 写入数据库
            analy_detail(content_dict, rec, ym)
            writeMonth(ym, content_dict, rec)
            content_dict = [{} for i in range(pageSize)]
            minutes, secs = divmod((datetime.now() - start_month_time).seconds, 60)
            print('\tProcessing..{:4d}条记录，用时:{:3d}秒，累计用时:{:2d}分{:2d}秒'.
                  format(rec + 1, (datetime.now() - start_page_time).seconds, minutes, secs))
            start_page_time = datetime.now()

    minutes, secs = divmod((datetime.now() - start_month_time).seconds, 60)
    print('处理{}年{}月数据，共{:^4d}条记录，统计用时:{:2d}分{:2d}秒'.format(ym[:4], ym[4:], total_rec, minutes, secs))


def analy_detail(content_dict, rec, ym):
    html = login_s.get(detail_url.format(rec + 1, ym), headers=login_headers,
                       cookies=requests.utils.cookiejar_from_dict(login_cookies_dict)).content.decode('gb18030')
    doc = pq(html)
    lines = doc('rec').html().replace('\r', '').split('\n')
    content_dict[rec % pageSize]['ID'] = rec
    content_dict[rec % pageSize]['Date'] = lines[1].split('=')[1].replace('.', '-')
    content_dict[rec % pageSize]['Layout'] = int(lines[2].split('=')[1])
    content_dict[rec % pageSize]['LayoutName'] = lines[3].split('=')[1]
    content_dict[rec % pageSize]['IntroTitle'] = lines[4].split('=')[1]
    content_dict[rec % pageSize]['Title'] = lines[5].split('=')[1]
    content_dict[rec % pageSize]['SubTitle'] = lines[6].split('=')[1]
    content_dict[rec % pageSize]['Writer'] = lines[7].split('=')[1]
    # 去除 <正文>= 与 <附图>=.. 这两行
    # 去除HTML标签，注意这里要保留住加粗显示，后面要再换回来
    content = '\n'.join(lines[9:-2]).replace('<b>', '[b]').replace('</b>', '[/b]')
    content = re.sub('<[^>]*>', '', content).replace('[b]', '<b>').replace('[/b]', '</b>')
    # 去除 %, %应该是没什么影响的。那就替换单引号吧。。。
    content_dict[rec % pageSize]['Content'] = content.replace('\'', '\'\'')


def get_multi_month(start_year, start_month, end_month):
    for m in range(start_month, end_month + 1):
        ym = '{}{:02d}'.format(start_year, m)
        get_month(ym)


if __name__ == '__main__':
    get_month('201901')
