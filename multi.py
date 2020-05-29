
# 想着改成多线程的，可以一次性处理四个月份的数据，那样的话，会不会快一些？2020-05-28 09:12:35
# 现在的处理方式是一次多运行多个程序，分别爬取不同的年份，好像也是可以的，但还是有点太麻烦了
from pyquery import PyQuery as pq
import requests
import calendar
import sqlite3
from datetime import datetime, timedelta

base_url = 'http://laoziliao.net/rmrb'
headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                         '(KHTML, like Gecko) Ubuntu Chromium/68.0.3440.106 Chrome/68.0.3440.106 Safari/537.36'}


def process_date(date_url, total, spec_date):
    date_dict = [dict() for i in range(0, total)]
    index_html = str(requests.get(date_url, headers=headers).content, 'utf-8')
    doc = pq(index_html)
    is_start_zero = False
    for k, v in enumerate(doc('.box li').items()):
        # 把题目前面的特殊符号去掉
        date_dict[k]['Title'] = v.text()[1:]
        date_dict[k]['Link'] = v('a').attr('href')
        date_dict[k]['Layout'] = int(getLayout(v('a').attr('href')))
        # 如果 Layout=0 那么就需要从0 开始计数
        if date_dict[k]['Layout'] == 0:
            is_start_zero = True
        date_dict[k]['Date'] = spec_date

    # 总的版面数，也就是有几个详情文件，而某一版面中的若干篇文章是存在于这一版上面的，通过 #xxxx 锚点来确定文章的详情
    # 2020-05-29 20:22:56 已经发现了原文中存在 Layout=0 的情况，那么在以下的循环中就取不到 Layout=0 的详情文件，会
    # 造成 date_dict[k]['Content'] 没有，那么在写入数据库的时候就会出错。。。
    totalLayout = int(date_dict[k]['Layout'])
    layout_range = range(0, totalLayout + 1) if is_start_zero else range(1, totalLayout + 1)
    for layout in layout_range:
        detail_url = '{}-{}'.format(date_url, layout)
        detail_doc = pq(requests.get(detail_url, headers=headers).content.decode('utf-8'))

        for k, v in enumerate(date_dict):
            # 从date_dict当中取出第n版，解析出每篇文章的#id
            if date_dict[k]['Layout'] == layout:
                # 取出 date_dict 对应的 #id
                tag_id = date_dict[k]['Link'][date_dict[k]['Link'].rindex('#') + 1:]
                # print('....{}'.format(date_dict[k]['Link']))
                content = detail_doc('#{}'.format(tag_id)).next().text().split('\n')
                # 去掉开头的3行
                date_dict[k]['Content'] = '\n'.join(content[3:])
                date_dict[k]['Title'] = detail_doc('#{}'.format(tag_id)).text()
    return date_dict


def getYear(year, num=0):
    def getOneYear(my_year):
        for m in range(5, 13):
            start_month_time = datetime.now()
            print('Processing...{}年{:02d}月'.format(my_year, m))
            date_sheets = getMonth('{}-{:02d}'.format(my_year, m))
            minutes, secs = divmod((datetime.now() - start_month_time).seconds, 60)
            print('{}年{:02d}月，{:^4d}篇文章，共计用时 {:2d}分{:>2d}秒'.format(my_year, m, date_sheets, minutes, secs))

    if num > 0:
        for y in range(int(year), int(year) + num + 1):
            getOneYear(y)
            print('-' * 50)
    else:
        getOneYear(year)


# 处理某一个月
# month的格式为：YYYY-MM
def getMonth(month):
    url = base_url + '/' + month
    index_html = str(requests.get(url, headers=headers).content, 'utf-8')
    doc = pq(index_html)
    month_dict = init_month_dict(month)
    total_sheet = 0
    # 主要是要处理有的日期可能是 0 篇，那么这些日期就不会有链接
    for k, v in enumerate(doc('.c_m p').items()):
        # 这里面含有‘篇’字，需要将其去掉
        if int(v.text()[:-1]) > 0:
            month_dict[k]['Quantity'] = int(v.text()[:-1])
    # 遍历带链接的那些内容，这些条目是少于“XX篇”这些的
    for item in doc('.c_m a').items():
        date = item.attr('href')[-10:]
        for k, v in enumerate(month_dict):
            if month_dict[k]['Date'] == date:
                month_dict[k]['Link'] = item.attr('href')

    for k, v in enumerate(month_dict):
        if month_dict[k]['Quantity'] > 0:
            # print(month_dict[k]['Quantity'], '\t', month_dict[k]['Link'])
            # 处理某一天的情况
            print('\tProcessing...{}, {:^4d}篇'.format(v['Date'], v['Quantity']), end=',')
            start_time = datetime.now()
            total_sheet += v['Quantity']
            date_dict = process_date(month_dict[k]['Link'], month_dict[k]['Quantity'], v['Date'])
            # print('date_dict''s length is:{}'.format(len(date_dict)))
            # 将每一天的字典内容写入到数据库中就可以了。。。2020-05-26 06:52:01
            # for k, v in enumerate(date_dict):
            writeMonth(date_dict, month)
            print(' 用时{:^4d}秒'.format((datetime.now() - start_time).seconds))
    return total_sheet


# 写入到sqlite表中
def writeMonth(month_dict, month):
    create_sql = 'CREATE TABLE if not exists `{}`( `id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, `Title` TEXT, `Link` TEXT, `Date` ' \
                 'TEXT, `Layout` INTEGER, `Content` TEXT)'
    add_sql = 'insert into `{}`(`Title`, `Link`, `Date`, `Layout`, `Content`) values("{}","{}","{}","{}","{}");'
    # 创建以年为单位的数据库，以月为单位的数据表，以文章为单位的数据条目记录
    conn = sqlite3.connect(month[:4] + '.db')
    cursor = conn.cursor()
    # cursor.execute('drop table {}'.format(month))
    cursor.execute(create_sql.format(month))
    cursor.execute('begin transaction')
    for k, v in enumerate(month_dict):
        try:
            cursor.execute(add_sql.format(month, v['Title'], v['Link'], v['Date'], v['Layout'], v['Content']))
        except sqlite3.Error as err:
            print('Error:{}, Link:{}, Content:{}'.format(err, v['Link'], v['Content']))
    cursor.execute('commit')
    cursor.close()
    conn.close()


# 通过给出的 URL 地址，解析所在版面
# 是在 YYYY-MM-DD-LL中的LL，有可能是1位，也有可能是两位，以#分隔后面的内容
# 从右边开始查找 # 的位置，及最末一个 - 的位置，两者之间即为版面数
def getLayout(url):
    return url[url.rindex('-') + 1:url.rindex('#')]


# 初始化月份索引字典列表
def init_month_dict(month):
    y = int(month[:4])
    m = int(month[5:])
    days_of_month = calendar.monthrange(y, m)[1]
    month_dict = [dict() for i in range(0, days_of_month)]
    for k, v in enumerate(month_dict):
        month_dict[k]['Quantity'] = 0
        month_dict[k]['Link'] = ''
        month_dict[k]['Date'] = '{}-{:02d}'.format(month, k + 1)

    return month_dict


if __name__ == '__main__':
    # getMonth('1946-07')
    # process_date(base_url + '/' + '1946-05-15', 38)
    getYear('1999')
