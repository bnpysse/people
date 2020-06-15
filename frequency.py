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
    'ezproxy': '7eni2MulcC5SVaf',
}
login_url = 'http://data.people.com.cn.proxy.library.georgetown.edu/rmrb/20200515/1?code=2'
login_headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu '
                               'Chromium/68.0.3440.106 Chrome/68.0.3440.106 Safari/537.36',
                 'Content-Type': 'text/html;charset=UTF-8', }
login_s = requests.session()
cookies = requests.utils.cookiejar_from_dict(login_cookies_dict)
login_s.get(login_url, headers=login_headers, cookies=cookies)
# endregion

date_start = '1993-01-01'
date_end = '2020-06-15'
pageSize = 50
database_name = 'words_frequency.db'

# region 查询串
base_url = 'http://data.people.com.cn.proxy.library.georgetown.edu/rmrb/s?qs='

# 两个词的情况
# 访问的时候是：qs_2['cds'][2..3]['cds'][0..3]['val'],第一标为两个关键字，第二标为四种不同的变量
qs_2 = {
    "cds": [{"fld": "dataTime.start", "cdr": "AND", "hlt": "false", "vlr": "AND", "qtp": "DEF", "val": date_start},
            {"fld": "dataTime.end", "cdr": "AND", "hlt": "false", "vlr": "AND", "qtp": "DEF", "val": date_end},
            {"cdr": "AND", "cds": [{"fld": "title", "cdr": "OR", "hlt": "true", "vlr": "OR", "val": "克林顿"},
                                   {"fld": "subTitle", "cdr": "   OR", "hlt": "true", "vlr": "OR", "val": "克林顿"},
                                   {"fld": "introTitle", "cdr": "OR", "hlt": "true", "vlr": "OR", "val": "克林顿"},
                                   {"fld": "contentText", "cdr": "OR", "hlt": "true", "vlr": "OR", "val": "克林顿"}]},
            {"cdr": "AND", "cds": [{"fld": "title", "cdr": "OR", "hlt": "true", "vlr": "OR", "val": "枪支"},
                                   {"fld": "subTitle", "cdr": "OR", "hlt": "true", "vlr": "OR", "val": "枪支"},
                                   {"fld": "introTitle", "cdr": "OR", "hlt": "true", "vlr": "OR", "val": "枪支"},
                                   {"fld": "contentText", "cdr": "OR", "hlt": "true", "vlr": "OR", "val": "枪支"}]}],
    "obs": [{"fld": "dataTime", "drt": "ASC"}]}

# 三个词的查询串
# 访问的时候是：qs_3['cds'][2..4]['cds'][0..3]['val'],第一标为三个关键字，第二标为四种不同的变量
qs_3 = {
    "cds": [{"fld": "dataTime.start", "cdr": "AND", "hlt": "false", "vlr": "AND", "qtp": "DEF", "val": date_start},
            {"fld": "dataTime.end", "cdr": "AND", "hlt": "false", "vlr": "AND", "qtp": "DEF", "val": date_end},
            {"cdr": "AND", "cds": [{"fld": "title", "cdr": "OR", "hlt": "true", "vlr": "OR", "val": "克林顿"},
                                   {"fld": "subTitle", "cdr": "OR", "hlt": "true", "vlr": "OR", "val": "克林顿"},
                                   {"fld": "introTitle", "cdr": "OR", "hlt": "true", "vlr": "OR", "val": "克林顿"},
                                   {"fld": "contentText", "cdr": "OR", "hlt": "true", "vlr": "OR", "val": "克林顿"}]},
            {"cdr": "AND", "cds": [{"fld": "title", "cdr": "OR", "hlt": "true", "vlr": "OR", "val": "枪支"},
                                   {"fld": "subTitle", "cdr": "OR", "hlt": "true", "vlr": "OR", "val": "枪支"},
                                   {"fld": "introTitle", "cdr": "OR", "hlt": "true", "vlr": "OR", "val": "枪支"},
                                   {"fld": "contentText", "cdr": "OR", "hlt": "true", "vlr": "OR", "val": "枪支"}]},
            {"cdr": "AND", "cds": [{"fld": "title", "cdr": "OR", "hlt": "true", "vlr": "OR", "val": "暴力"},
                                   {"fld": "subTitle", "cdr": "OR", "hlt": "true", "vlr": "OR", "val": "暴力"},
                                   {"fld": "introTitle", "cdr": "OR", "hlt": "true", "vlr": "OR", "val": "暴力"},
                                   {"fld": "contentText", "cdr": "OR", "hlt": "true", "vlr": "OR", "val": "暴力"}]}],
    "obs": [{"fld": "dataTime", "drt": "ASC"}]}

base_url_tail = '&tr=A&ss=1&pageNo={}&pageSize={}'


# endregion

# region Word list, and combine of word list AB,AC,ABC
def read_word_list(filename):
    with open(filename) as f:
        lines = f.readlines()
        a = [line.rstrip() for line in lines[0].split(',')]
        b = [line.rstrip() for line in lines[1].split(',')]
        c = [line.rstrip() for line in lines[2].split(',')]
    return a, b, c


# endregion

# region 生成组合词组
def building_qs(*args):
    combination_list = list(itertools.product(*args))
    for word in combination_list:
        if len(args) == 2:
            for i in range(4):
                qs_2['cds'][2]['cds'][i]['val'] = word[0]
                qs_2['cds'][3]['cds'][i]['val'] = word[1]
            yield word, base_url + urllib.parse.quote(str(qs_2).replace('\'', '\"')) + base_url_tail
        elif len(args) == 3:
            for i in range(4):
                qs_3['cds'][2]['cds'][i]['val'] = word[0]
                qs_3['cds'][3]['cds'][i]['val'] = word[1]
                qs_3['cds'][4]['cds'][i]['val'] = word[2]
            yield word, base_url + urllib.parse.quote(str(qs_3).replace('\'', '\"')) + base_url_tail


# endregion

def get_word_frequency(table_name, *args):
    create_sqlite_db(table_name)
    # layout、Count为数值型 ！！
    insert_sql = 'insert into `{}`(Title, Date, Keywords, MyWords, Layout, Count, Summary) values("{}","{}","{}","{}", {}, {},"{}")'
    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()
    start_time = datetime.now()
    gen = building_qs(*args)
    pageNo = 1
    while True:
        try:
            keywords, url = next(gen)
            # 首先取出第1页的内容，然后获得总的页数，再取剩余的页的内容
            try:
                response = login_s.get(url.format(pageNo, pageSize), headers=login_headers,
                                       cookies=cookies).content.decode('utf-8')
                doc = pq(response)
            except Exception as e:
                print(e)
                pass
            total_record_num = int(doc('#allDataCount').text())
            page_total = math.ceil(total_record_num / pageSize)
            for page in range(1, page_total + 1):
                start_page_time = datetime.now()
                content_dict = [dict() for i in range(pageSize)]
                try:
                    response = login_s.get(url.format(page, pageSize), headers=login_headers,
                                           cookies=cookies).content.decode('utf-8')
                    doc = pq(response)
                except Exception as e:
                    print(e)
                    pass
                for k, v in enumerate(doc('.sreach_li').items()):
                    # 标题： doc('.sreach_li')('h3').text()
                    # 日期： doc('.listinfo').eq(42).text()[:doc('.listinfo').eq(42).text().rindex('日') + 1]
                    # 版次： re.findall('第(\d+)版', doc('.listinfo').eq(49).text())
                    # 摘要： doc('.listinfo').eq(42).next()('p').text()
                    # 文章关键词：doc('.keywords').text()
                    content_dict[k]['Title'] = v('h3').text()
                    public_date = v('.listinfo').text()
                    content_dict[k]['Date'] = public_date[:public_date.rindex('日') + 1]
                    content_dict[k]['Layout'] = int(re.findall('第(\d+)版', v('.listinfo').text())[0])
                    content_dict[k]['Summary'] = v('.listinfo').next()('p').html().replace('\n', '').replace('\t', '')
                    content_dict[k]['Keywords'] = v('.keywords').text()[7:]
                    content_dict[k]['Count'] = total_record_num
                    content_dict[k]['MyWords'] = ' '.join(keywords)

                # 将content_dict写入数据库即可
                try:
                    cursor.execute('begin transaction')
                    for k, v in enumerate(content_dict):
                        if 'Title' in content_dict[k].keys():
                            cursor.execute(
                                insert_sql.format(table_name, content_dict[k]['Title'], content_dict[k]['Date'],
                                                  content_dict[k]['Keywords'], content_dict[k]['MyWords'],
                                                  content_dict[k]['Layout'], content_dict[k]['Count'],
                                                  content_dict[k]['Summary']))
                    cursor.execute('commit')
                    print('Processing..{}, 第{:>2d}页,用时：{:5.2f}秒'.format('+'.join(keywords), page,
                                                                        (datetime.now() - start_page_time).seconds))
                except Exception as e:
                    print(e)
                    tmp_string = insert_sql.format(table_name, content_dict[k]['Title'], content_dict[k]['Date'],
                                                   content_dict[k]['Keywords'], content_dict[k]['Count'],
                                                   content_dict[k]['Summary'])
                    print(tmp_string)
                    cursor.execute('rollback')

        except StopIteration as e:
            print('Generator is done:', e.value)
            minutes, secs = divmod((datetime.now() - start_time).seconds, 60)
            print('总计用时:{:2d}分{:>3d}秒'.format(minutes, secs))
            cursor.close()
            conn.close()
            break


def create_sqlite_db(table_name):
    sql = 'CREATE TABLE if not exists `{}`( `id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, `Title` TEXT, `Date` ' \
          'TEXT, `Keywords` TEXT, `Count` INTEGER, `Summary` TEXT )'
    # delete_sql = 'drop table {}'
    conn = sqlite3.connect(database_name)
    cur = conn.cursor()
    cur.execute(sql.format(table_name))
    cur.close()
    conn.commit()
    conn.close()


if __name__ == '__main__':
    A, B, C = read_word_list('.word_list.txt')
    get_word_frequency(A, B, 'AB')
