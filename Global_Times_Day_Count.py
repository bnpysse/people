# http://43.250.238.143.proxy.library.georgetown.edu/search?channelid=12900&searchword=%C8%D5%C6%DA%3d1993.01.03
# login_url:  http://43.250.238.143.proxy.library.georgetown.edu/directLogin.do
# 对于Global Times而言，可以用这个地址来获取每一天的文章数目，不过由于此刊前期是周刊，并不知晓哪一天有文章，故此，从
# 1993年01月03开始，要对没有文章的日期进行判断，同时，还要注意判断闰年的情况，etc...

import requests
from pyquery import PyQuery as pq

# region 更改 cookie 值，每次当程序不能正确运行时，需要修改这里的 ezproxy
# 获取正确的对话 login_session
login_cookies_dict = {
    '_ga': 'GA1.2.1306172715.1609485446',
    # 只需要改这个东东就可以，2020-06-11 17:14:42
    'ezproxy': '57vAYi2LpR6UHQT',
    # 这个 userid 和 pass, 应该是不用做任何改动，2020-01-02 14：10：45
    'pass': '11%2C101%2C103%2C104%2C105%2C107%2C114%2C129%2C',
    'userid': 'georgetownuc',
}

start_date = '1993.01.03'
base_url = 'http://43.250.238.143.proxy.library.georgetown.edu/search?channelid=12900&searchword=%C8%D5%C6%DA%3d{}'
# base_url = 'http://43.250.238.143.proxy.library.georgetown.edu/search'
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

response = login_s.get(base_url.format(start_date), headers=login_headers, cookies=cookies).content.decode('GB2312')
doc = pq(response)
print(doc('font').text() + '条记录')
