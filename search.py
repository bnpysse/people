import itertools
import re
import sqlite3
import urllib.parse
from datetime import datetime
import pprint
import requests
from pyquery import PyQuery as pq

login_cookies_dict = {
    '_ga': 'GA1.2.576373095.1589077068',
    # 只需要改这个东东就可以，2020-06-11 17:14:42
    'ezproxy': 'BosUt2d5p0TWQrw',
}

login_url = 'http://data.people.com.cn.proxy.library.georgetown.edu/rmrb/20200515/1?code=2'

login_headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu '
                               'Chromium/68.0.3440.106 Chrome/68.0.3440.106 Safari/537.36',
                 'Content-Type': 'text/html;charset=UTF-8', }

post_headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu '
                              'Chromium/68.0.3440.106 Chrome/68.0.3440.106 Safari/537.36',
                'Content-Type': 'application/x-www-form-urlencoded', }
login_s = requests.session()
cookies = requests.utils.cookiejar_from_dict(login_cookies_dict)
login_s.get(login_url, headers=login_headers, cookies=cookies)

# region Word list, and combine of word list AB,AC,ABC
A = []
B = []
C = []
# endregion

date_start = '1993-01-01'
date_end = '2020-06-11'
pageSize = 20
database_name = 'words_frequency.db'
base_url = 'http://data.people.com.cn.proxy.library.georgetown.edu/sc/ss?qs='
base_url_tail = '&title=&title={}title=&dateTimeStart={}&dateTimeEndt={}&checkbox_sel=23&cIds='

# region 从 chrome 中获取的查询串
qs = {"cIds": "23,", "cds": [
    {"cdr": "AND", "cds": [
        {"fld": "dataTime.start", "cdr": "AND", "hlt": "false", "vlr": "OR", "val": date_start},
        {"fld": "dataTime.end", "cdr": "AND", "hlt": "false", "vlr": "OR", "val": date_end}]},
    {"cdr": "AND", "cds": [
        {"cdr": "AND", "cds": [
            {"cdr": "AND",
             "cds": [{"fld": "title", "cdr": "OR", "hlt": "true", "vlr": "AND", "val": "克林顿"},
                     {"fld": "subTitle", "cdr": "OR", "hlt": "true", "vlr": "AND", "val": "克林顿"},
                     {"fld": "introTitle", "cdr": "OR", "hlt": "true", "vlr": "AND", "val": "克林顿"},
                     {"fld": "contentText", "cdr": "OR", "hlt": "true", "vlr": "AND", "val": "克林顿"}]},
            {"cdr": "AND",
             "cds": [{"fld": "title", "cdr": "OR", "hlt": "true", "vlr": "AND", "val": "暴力"},
                     {"fld": "subTitle", "cdr": "OR", "hlt": "true", "vlr": "AND", "val": "暴力"},
                     {"fld": "introTitle", "cdr": "OR", "hlt": "true", "vlr": "AND", "val": "暴力"},
                     {"fld": "contentText", "cdr": "OR", "hlt": "true", "vlr": "AND", "val": "暴力"}]}]}]}],
      "obs": [{"fld": "dataTime", "drt": "DESC"}, {"fld": "orderId", "drt": "DESC"}, {"fld": "seqid", "drt": "DESC"}]}


# endregion

# region 测试查询字典的关键字位置
# print(urllib.parse.urlencode(qs))
# print(str(qs).replace('\'', '\"'))
# print(urllib.parse.quote(str(qs).replace('\'', '\"')))
# # 第一个关键字
# print('{}'.format(qs['cds'][1]['cds'][0]['cds'][0]['cds'][0]['val']))  # title
# print('{}'.format(qs['cds'][1]['cds'][0]['cds'][0]['cds'][1]['val']))  # subTitle
# print('{}'.format(qs['cds'][1]['cds'][0]['cds'][0]['cds'][2]['val']))  # introTitle
# print('{}'.format(qs['cds'][1]['cds'][0]['cds'][0]['cds'][3]['val']))  # contentText
# # 第二个关键字
# print('{}'.format(qs['cds'][1]['cds'][0]['cds'][1]['cds'][0]['val']))
# print('{}'.format(qs['cds'][1]['cds'][0]['cds'][1]['cds'][1]['val']))
# print('{}'.format(qs['cds'][1]['cds'][0]['cds'][1]['cds'][2]['val']))
# print('{}'.format(qs['cds'][1]['cds'][0]['cds'][1]['cds'][3]['val']))
# endregion


def building_qs(word_list1, word_list2):
    combination_list = list(itertools.product(word_list1, word_list2))
    for word in combination_list:
        # 之所以四次循环，是把title,subTitle,introTitle,contentText四个字段都赋值
        for i in range(4):
            qs['cds'][1]['cds'][0]['cds'][0]['cds'][i]['val'] = word[0]
            qs['cds'][1]['cds'][0]['cds'][1]['cds'][i]['val'] = word[1]
        yield (word[0], word[1]), base_url + urllib.parse.quote(str(qs).replace('\'', '\"'))


def get_word_frequency(word_list1, word_list2, table_name):
    count = 0
    create_sqlite_db(table_name)
    insert_sql = 'insert into `{}`(Title, Date, Keywords, Count, Summary) values("{}","{}","{}",{},"{}")'
    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()
    start_time = datetime.now()
    gen = building_qs(word_list1, word_list2)
    while True:
        try:
            keywords, url = next(gen)
            # 首先取出第1页的内容，然后获得总的页数，再取剩余的页的内容
            form_data = {'pageNo': 1, 'pageSize': pageSize}
            response = login_s.post(url, data=form_data, headers=post_headers, cookies=cookies).content.decode('utf-8')
            doc = pq(response)
            counter_string = doc('.pagination').text()
            rec = re.findall('共( \d+ )条', counter_string)
            page_total_string = re.findall('共( \d+ )页', counter_string)
            page_total = int(page_total_string[0])
            for page in range(1, page_total + 1):
                start_page_time = datetime.now()
                form_data['pageNo'] = page
                content_dict = [dict() for i in range(pageSize)]
                response = login_s.post(url, data=form_data, headers=post_headers, cookies=cookies).content.decode(
                    'utf-8')
                doc = pq(response)
                for k, v in enumerate(doc('.articleSum_li').items()):
                    # 直接取出该Tag下的所有文本，并分隔成字符串列表
                    # 最末一项为‘来源： 人民日报 时间：。。。。’
                    # 倒数第二项为简要
                    # 剩余的内容组合成Title，因为有的时候Title会是两种不同的Tag来标识的
                    lines = v.text().split('\n')
                    content_dict[k]['Date'] = lines.pop(-1)[-10:]
                    content_dict[k]['Summary'] = re.sub('<a href.*', '',
                                                        v('p').html().
                                                        replace('\t', '').replace('\n', '').
                                                        replace('\"', '').replace('\'', ''))
                    lines.pop(-1)
                    content_dict[k]['Title'] = '\n'.join(lines)
                    content_dict[k]['Count'] = int(rec[0])
                    content_dict[k]['Keywords'] = ' '.join(keywords)

                # 将content_dict写入数据库即可
                try:
                    cursor.execute('begin transaction')
                    for k, v in enumerate(content_dict):

                        if 'Title' in content_dict[k].keys():
                            cursor.execute(
                                insert_sql.format(table_name, content_dict[k]['Title'], content_dict[k]['Date'],
                                                  content_dict[k]['Keywords'], content_dict[k]['Count'],
                                                  content_dict[k]['Summary']))
                    cursor.execute('commit')
                    print('Processing..{}, 第{:>2d}页,用时：{:5.2f}秒'.format('+'.join(keywords), page,
                                                                        (datetime.now() - start_page_time).seconds))
                    count += 1
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
    get_word_frequency(A, B, 'AB')
