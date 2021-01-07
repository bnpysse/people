# http://43.250.238.143.proxy.library.georgetown.edu/search?channelid=12900&searchword=%C8%D5%C6%DA%3d1993.01.03
# login_url:  http://43.250.238.143.proxy.library.georgetown.edu/directLogin.do
# 对于Global Times而言，可以用这个地址来获取每一天的文章数目，不过由于此刊前期是周刊，并不知晓哪一天有文章，故此，从
# 1993年01月03开始，要对没有文章的日期进行判断，同时，还要注意判断闰年的情况，etc...
import sqlite3
from datetime import datetime

import requests
from pyquery import PyQuery as pq
import calendar

# region 更改 cookie 值，每次当程序不能正确运行时，需要修改这里的 ezproxy
# 获取正确的对话 login_session
login_cookies_dict = {
    '_ga': 'GA1.2.1306172715.1609485446',
    # 只需要改这个东东就可以，2020-06-11 17:14:42
    'ezproxy': '8efELFEP5NMk14z',
    # 这个 userid 和 pass, 应该是不用做任何改动，2020-01-02 14：10：45
    'pass': '11%2C101%2C103%2C104%2C105%2C107%2C114%2C129%2C',
    'userid': 'georgetownuc',
}

start_date = '1993.01.03'
# 最大期号，对应的日期是 2021.01.04
start_isssue_number = 526
max_issue_number = 5256
database_name = 'Global_Times.db'
my_table_name = 'issue_count'
pageSize = 25

# base_url = 'http://43.250.238.143.proxy.library.georgetown.edu/search?channelid=12900&searchword=%C8%D5%C6%DA%3d{}'
# base_url = 'http://43.250.238.143.proxy.library.georgetown.edu/search'

# 这里在 %3D 之后，以及 Field1= 之后的值，即为期号，IssueNumber，哈哈，解决了！！！ 2020-01-04 20：23：30
base_url = ('http://43.250.238.143.proxy.library.georgetown.edu/search?channelid=12900&'
            'searchword=%C6%DA%BA%C5%3D{}&channelid=129&Field1={}&image2.x=16&image2.y=12')

login_url = 'http://43.250.238.143.proxy.library.georgetown.edu/directLogin.do'
login_headers = {
    'Accept': 'text/html,application/xhtml+xml,application3Cojg88u4rREqf1/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu '
                  'Chromium/68.0.3440.106 Chrome/68.0.3440.106 Safari/537.36',
    'Content-Type': 'text/html;charset=UTF-8', }

login_s = requests.session()
cookies = requests.utils.cookiejar_from_dict(login_cookies_dict)
login_s.get(login_url, headers=login_headers, cookies=cookies)


# endregion


def create_sqlite_db(table_name):
    sql = 'CREATE TABLE if not exists `{}`( `id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, `Date` ' \
          'TEXT, `IssueNumber` INTEGER, `Count` INTEGER)'
    # delete_sql = 'drop table {}'
    conn = sqlite3.connect(database_name)
    cur = conn.cursor()
    cur.execute(sql.format(table_name))
    # 创建自 start_date 开始的空数据表
    # 知道每个月的最后一天？

    cur.close()
    conn.commit()
    conn.close()


def get_issue_count():
    i, k = start_isssue_number, 0
    insert_sql = 'insert into `{}`(Date, IssueNumber, Count) values("{}",{},{})'
    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()
    start_time = datetime.now()
    rec_dict = [dict() for k in range(pageSize)]
    while i <= max_issue_number:
        response = login_s.get(base_url.format(i, i), headers=login_headers, cookies=cookies).content.decode('gb18030')
        doc = pq(response)

        count = int(doc('font').text())
        if count == 0:
            # 没有记录的情况
            rec_dict[k]['riqi'] = '0000.00.00'
            rec_dict[k]['count'] = 0
            rec_dict[k]['issue_number'] = i
        else:
            # 要在 doc 中找到 script 脚本，其中有日期项目，其标识符为 [-12:-2]
            riqi = doc.find('script')[3].text.strip().split('\r\n')[2][-12:-2]
            rec_dict[k]['riqi'] = riqi
            rec_dict[k]['issue_number'] = i
            rec_dict[k]['count'] = count
        print(rec_dict[k]['riqi'], '--', rec_dict[k]['issue_number'], '--', rec_dict[k]['count'])
        if i % pageSize == 0:
            # 写入数据库中
            try:
                cursor.execute('begin transaction')
                for k, v in enumerate(rec_dict):
                    cursor.execute(insert_sql.format(my_table_name, rec_dict[k]['riqi'], rec_dict[k]['issue_number'],
                                                     rec_dict[k]['count']))
                cursor.execute('commit')
                k = 0
                rec_dict = [dict() for k in range(pageSize)]
                print('Processing {} recod.'.format(pageSize))
                i += 1
                continue
            except Exception as e:
                print(e)
        i += 1
        k += 1
        # print('第{:5d}期 -- 文章数目{} -- 日期{}'.format(i, doc('font').text(), riqi))


if __name__ == '__main__':
    create_sqlite_db(my_table_name)
    get_issue_count()
